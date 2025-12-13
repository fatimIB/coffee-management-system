from concurrent import futures
import grpc
from datetime import datetime
from dotenv import load_dotenv
from database.db_connection import get_connection
import grpc
from shared_proto import order_pb2, order_pb2_grpc
from shared_proto import inventory_pb2, inventory_pb2_grpc

load_dotenv()

class OrderServiceServicer(order_pb2_grpc.OrderServiceServicer):
    def __init__(self):
        self.conn = get_connection()
        if not self.conn:
            raise Exception("Database connection not available")
    
    def CreateOrder(self, request, context):
        """
        Crée une commande avec ses items
        1. Crée la commande dans orders
        2. Crée les order_items
        3. Met à jour l'inventaire via Inventory Service
        4. Envoie les logs vers Analytics (insertion dans analytics_logs)
        """
        try:
            cursor = self.conn.cursor()
            cafe_id = int(request.cafe_id)
            total_price = sum(item.price * item.quantity for item in request.items)
            
            # 1. Créer la commande
            insert_order_query = """
                INSERT INTO orders (cafe_id, total_price, created_at)
                VALUES (%s, %s, %s)
            """
            created_at = datetime.now()
            cursor.execute(insert_order_query, (cafe_id, total_price, created_at))
            order_id = cursor.lastrowid
            
            # 2. Créer les order_items et mettre à jour l'inventaire
            inventory_channel = grpc.insecure_channel('inventory_service:5006')
            inventory_stub = inventory_pb2_grpc.InventoryServiceStub(inventory_channel)
            
            for item in request.items:
                item_id = int(item.item_id)
                quantity = item.quantity
                price = item.price
                
                # Insérer order_item
                insert_item_query = """
                    INSERT INTO order_items (order_id, item_id, quantity, price)
                    VALUES (%s, %s, %s, %s)
                """
                cursor.execute(insert_item_query, (order_id, item_id, quantity, price))
                
                # 3. Mettre à jour l'inventaire via gRPC
                try:
                    update_request = inventory_pb2.UpdateInventoryRequest(
                        item_id=str(item_id),
                        cafe_id=str(cafe_id),
                        quantity_ordered=quantity
                    )
                    inventory_response = inventory_stub.UpdateInventoryAfterOrder(update_request)
                    
                    if not inventory_response.success:
                        # Rollback si stock insuffisant
                        self.conn.rollback()
                        inventory_channel.close()
                        context.set_code(grpc.StatusCode.FAILED_PRECONDITION)
                        context.set_details(f"Insufficient stock for item {item_id}")
                        return order_pb2.CreateOrderResponse(
                            success=False,
                            message=f"Insufficient stock for item {item_id}"
                        )
                except Exception as e:
                    print(f"Error updating inventory: {e}")
                    self.conn.rollback()
                    inventory_channel.close()
                    context.set_code(grpc.StatusCode.INTERNAL)
                    context.set_details(f"Error updating inventory: {str(e)}")
                    return order_pb2.CreateOrderResponse(
                        success=False,
                        message=f"Error updating inventory: {str(e)}"
                    )
                
                # 4. Envoyer les logs vers Analytics (insertion dans analytics_logs)
                try:
                    insert_analytics_query = """
                        INSERT INTO analytics_logs (order_id, cafe_id, item_id, quantity, total_price, timestamp)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """
                    item_total = price * quantity
                    cursor.execute(insert_analytics_query, (
                        order_id, cafe_id, item_id, quantity, item_total, created_at
                    ))
                except Exception as e:
                    print(f"Warning: Could not insert analytics log: {e}")
                    # Continue even if analytics log fails
            
            inventory_channel.close()
            self.conn.commit()
            cursor.close()
            
            return order_pb2.CreateOrderResponse(
                success=True,
                message="Order created successfully",
                order_id=str(order_id),
                total_price=total_price
            )
            
        except Exception as e:
            self.conn.rollback()
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error creating order: {str(e)}")
            return order_pb2.CreateOrderResponse(
                success=False,
                message=f"Error creating order: {str(e)}"
            )
    
    def GetOrdersByCafe(self, request, context):
        """Récupère toutes les commandes d'un café"""
        try:
            cursor = self.conn.cursor(dictionary=True)
            cafe_id = int(request.cafe_id)
            
            # Récupérer les commandes
            orders_query = """
                SELECT order_id, cafe_id, total_price, created_at
                FROM orders
                WHERE cafe_id = %s
                ORDER BY created_at DESC
            """
            cursor.execute(orders_query, (cafe_id,))
            orders = cursor.fetchall()
            
            response = order_pb2.OrdersResponse()
            
            for order_row in orders:
                order = response.orders.add()
                order.order_id = str(order_row['order_id'])
                order.cafe_id = str(order_row['cafe_id'])
                order.total_price = float(order_row['total_price'])
                order.created_at = str(order_row['created_at'])
                
                # Récupérer les items de la commande
                items_query = """
                    SELECT item_id, quantity, price
                    FROM order_items
                    WHERE order_id = %s
                """
                cursor.execute(items_query, (order_row['order_id'],))
                items = cursor.fetchall()
                
                for item_row in items:
                    item = order.items.add()
                    item.item_id = str(item_row['item_id'])
                    item.quantity = item_row['quantity']
                    item.price = float(item_row['price'])
            
            cursor.close()
            return response
            
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error fetching orders: {str(e)}")
            return order_pb2.OrdersResponse()

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    order_pb2_grpc.add_OrderServiceServicer_to_server(OrderServiceServicer(), server)
    server.add_insecure_port('[::]:5002')
    server.start()
    print("✅ Order Service running on port 5002")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
