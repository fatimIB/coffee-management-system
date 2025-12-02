from concurrent import futures
import grpc
import os
import sys
from dotenv import load_dotenv

# Import proto files
from proto import inventory_pb2, inventory_pb2_grpc

# Add database directory to path for connection.
# En local (hors Docker), on utilisera le chemin relatif au projet.
# En Docker, on suppose que le volume /app/database est monté dans le docker-compose.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LOCAL_DB_PATH = os.path.join(PROJECT_ROOT, "database")
if os.path.isdir(LOCAL_DB_PATH):
    sys.path.insert(0, LOCAL_DB_PATH)
else:
    # Fallback Docker path
    sys.path.insert(0, '/app/database')

from db_connection import get_connection

load_dotenv()

class InventoryServiceServicer(inventory_pb2_grpc.InventoryServiceServicer):
    def __init__(self):
        self.conn = get_connection()
        if not self.conn:
            raise Exception("Database connection not available")
    
    def GetInventoryByCafe(self, request, context):
        """Récupère la liste d'inventaire pour affichage dans le Frontend (Admin)"""
        try:
            cursor = self.conn.cursor(dictionary=True)
            
            # Query to get inventory with item names and cafe names
            query = """
                SELECT 
                    i.inventory_id,
                    i.item_id,
                    i.cafe_id,
                    m.name AS item_name,
                    c.name AS cafe_name,
                    i.stock AS stock_quantity,
                    i.restock_date,
                    CASE WHEN i.stock < 20 THEN 1 ELSE 0 END AS is_low_stock
                FROM inventory i
                JOIN menu_items m ON i.item_id = m.item_id
                JOIN cafes c ON i.cafe_id = c.cafe_id
                ORDER BY c.name, m.name
            """
            
            cursor.execute(query)
            results = cursor.fetchall()
            cursor.close()
            
            # Build response
            response = inventory_pb2.InventoryListResponse()
            
            for row in results:
                item = response.items.add()
                item.item_id = str(row['item_id'])
                item.cafe_id = str(row['cafe_id'])
                item.item_name = row['item_name']
                item.cafe_name = row['cafe_name']
                item.stock_quantity = int(row['stock_quantity'])
                item.restock_date = str(row['restock_date'])
                item.is_low_stock = bool(row['is_low_stock'])
            
            return response
            
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error fetching inventory: {str(e)}")
            return inventory_pb2.InventoryListResponse()
    
    def UpdateInventoryAfterOrder(self, request, context):
        """Met à jour le stock après une commande (Appel interne par Order Service)"""
        try:
            cursor = self.conn.cursor()
            
            # Update stock by subtracting quantity_ordered
            query = """
                UPDATE inventory 
                SET stock = stock - %s 
                WHERE item_id = %s AND cafe_id = %s AND stock >= %s
            """
            
            cursor.execute(query, (
                request.quantity_ordered,
                request.item_id,
                request.cafe_id,
                request.quantity_ordered
            ))
            
            self.conn.commit()
            success = cursor.rowcount > 0
            cursor.close()
            
            if success:
                return inventory_pb2.UpdateInventoryResponse(
                    success=True,
                    message="Inventory updated successfully"
                )
            else:
                return inventory_pb2.UpdateInventoryResponse(
                    success=False,
                    message="Insufficient stock or item not found"
                )
                
        except Exception as e:
            self.conn.rollback()
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error updating inventory: {str(e)}")
            return inventory_pb2.UpdateInventoryResponse(
                success=False,
                message=f"Error: {str(e)}"
            )
    
    def RestockItem(self, request, context):
        """Gère le réapprovisionnement (Appel par la Gateway suite à l'action Admin)"""
        try:
            cursor = self.conn.cursor()
            
            # Update stock by adding quantity_added and update restock_date
            query = """
                UPDATE inventory 
                SET stock = stock + %s, restock_date = %s
                WHERE item_id = %s AND cafe_id = %s
            """
            
            cursor.execute(query, (
                request.quantity_added,
                request.restock_date,
                request.item_id,
                request.cafe_id
            ))
            
            self.conn.commit()
            success = cursor.rowcount > 0
            cursor.close()
            
            if success:
                return inventory_pb2.RestockItemResponse(
                    success=True,
                    message="Item restocked successfully"
                )
            else:
                return inventory_pb2.RestockItemResponse(
                    success=False,
                    message="Item not found"
                )
                
        except Exception as e:
            self.conn.rollback()
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error restocking item: {str(e)}")
            return inventory_pb2.RestockItemResponse(
                success=False,
                message=f"Error: {str(e)}"
            )


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    inventory_pb2_grpc.add_InventoryServiceServicer_to_server(
        InventoryServiceServicer(), server
    )
    server.add_insecure_port('[::]:5006')
    print("Inventory gRPC server running on port 5006...")
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
