import grpc
from shared_proto import menu_pb2, menu_pb2_grpc

# Create gRPC channel and stub once
channel = grpc.insecure_channel('menu_service:5005')
stub = menu_pb2_grpc.MenuServiceStub(channel)

def get_menu_items(search=""):
    try:
        response = stub.GetMenuItems(menu_pb2.Empty())
        items = []
        for item in response.items:
            # Filter by search if provided
            if search and search.lower() not in item.name.lower():
                continue
            items.append({
                "id": item.id,
                "name": item.name,
                "category": item.category,
                "price": item.price
            })
        return items
    except grpc.RpcError as e:
        print(f"gRPC Error in get_menu_items: {e.code()} - {e.details()}")
        return []

def add_menu_item(name, category, price):
    try:
        item = menu_pb2.MenuItemRequest(name=name, category=category, price=price)
        response = stub.AddMenuItem(item)
        return {"id": response.id, "name": response.name, "category": response.category, "price": response.price}
    except grpc.RpcError as e:
        print(f"gRPC Error in add_menu_item: {e.code()} - {e.details()}")
        return None

def update_menu_item(id, name, category, price):
    try:
        item = menu_pb2.MenuItemRequest(id=id, name=name, category=category, price=price)
        response = stub.UpdateMenuItem(item)
        return {"id": response.id, "name": response.name, "category": response.category, "price": response.price}
    except grpc.RpcError as e:
        print(f"gRPC Error in update_menu_item: {e.code()} - {e.details()}")
        return None

def delete_menu_item(id):
    try:
        response = stub.DeleteMenuItem(menu_pb2.MenuItemRequest(id=id))
        return response.success
    except grpc.RpcError as e:
        print(f"gRPC Error in delete_menu_item: {e.code()} - {e.details()}")
        return False
