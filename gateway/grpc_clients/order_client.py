import grpc
from shared_proto import order_pb2, order_pb2_grpc

# Create gRPC channel and stub once
channel = grpc.insecure_channel('order_service:5002')
stub = order_pb2_grpc.OrderServiceStub(channel)

def create_order(cafe_id, items):
    """
    Create an order with items
    items: list of dicts with item_id, quantity, price
    """
    try:
        request = order_pb2.CreateOrderRequest(cafe_id=str(cafe_id))
        
        for item in items:
            order_item = request.items.add()
            order_item.item_id = str(item['item_id'])
            order_item.quantity = item['quantity']
            order_item.price = float(item['price'])
        
        response = stub.CreateOrder(request)
        return {
            "success": response.success,
            "message": response.message,
            "order_id": response.order_id,
            "total_price": response.total_price
        }
    except grpc.RpcError as e:
        print(f"gRPC Error in create_order: {e.code()} - {e.details()}")
        return {
            "success": False,
            "message": f"gRPC Error: {e.details()}"
        }

def get_orders_by_cafe(cafe_id):
    """Get all orders for a cafe"""
    try:
        request = order_pb2.GetOrdersRequest(cafe_id=str(cafe_id))
        response = stub.GetOrdersByCafe(request)
        
        orders = []
        for order in response.orders:
            items = []
            for item in order.items:
                items.append({
                    "item_id": item.item_id,
                    "quantity": item.quantity,
                    "price": item.price
                })
            
            orders.append({
                "order_id": order.order_id,
                "cafe_id": order.cafe_id,
                "total_price": order.total_price,
                "created_at": order.created_at,
                "items": items
            })
        
        return orders
    except grpc.RpcError as e:
        print(f"gRPC Error in get_orders_by_cafe: {e.code()} - {e.details()}")
        return []

