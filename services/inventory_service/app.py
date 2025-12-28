import sys
import os
import time
import random
import string
import requests
import grpc
from datetime import datetime

# ----------------------
# Adjust path to see shared_proto
# ----------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

# ----------------------
# Import gRPC modules
# ----------------------
from shared_proto import (
    order_pb2, order_pb2_grpc,
    cafe_pb2, cafe_pb2_grpc,
    login_pb2, login_pb2_grpc,
    adminlogin_pb2, adminlogin_pb2_grpc,
    menu_pb2, menu_pb2_grpc,
    inventory_pb2, inventory_pb2_grpc
)

# ----------------------
# CONFIGURATION
# ----------------------
BASE_URL = "http://localhost:5000"

GRPC_ADDRESSES = {
    "order": "localhost:5002",
    "login": "localhost:5001",
    "admin": "localhost:50011",
    "cafe": "localhost:5004",
    "inventory": "localhost:5006",
    "menu": "localhost:5005"
}

TEST_CAFE_ID = 1
TEST_ITEM_ID = 1
TEST_ITEM_PRICE = 10.0
TEST_USER_ACCESS = "DK456"
NUM_REQUESTS = 20

# ----------------------
# HELPERS
# ----------------------
def random_string(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def print_stats(service_name, times):
    if times:
        avg_time = sum(times) / len(times)
        max_time = max(times)
        min_time = min(times)
        print(f"\n=== Statistiques pour {service_name} ===")
        print(f"Temps moyen: {avg_time:.4f} sec")
        print(f"Temps max: {max_time:.4f} sec")
        print(f"Temps min: {min_time:.4f} sec\n")

# ----------------------
# REST TEST FUNCTIONS
# ----------------------
def rest_orders():
    print("\n--- REST Orders ---")
    response_times = []
    for i in range(NUM_REQUESTS):
        payload = {
            "cafe_id": TEST_CAFE_ID,
            "items": [{"item_id": TEST_ITEM_ID, "quantity": 1, "price": TEST_ITEM_PRICE}]
        }
        start_time = time.time()
        try:
            res = requests.post(f"{BASE_URL}/orders/create", json=payload)
            duration = time.time() - start_time
            response_times.append(duration)
            print(f"Request {i+1}: {res.status_code}")
        except Exception as e:
            duration = time.time() - start_time
            response_times.append(duration)
            print(f"Request {i+1} Error:", e)
    print_stats("REST Orders", response_times)

def rest_user_login():
    print("\n--- REST User Login ---")
    response_times = []
    for i in range(NUM_REQUESTS):
        payload = {"cafe_id": TEST_CAFE_ID, "access_code": TEST_USER_ACCESS}
        start_time = time.time()
        try:
            res = requests.post(f"{BASE_URL}/api/login", json=payload)
            duration = time.time() - start_time
            response_times.append(duration)
            print(f"Request {i+1}: {res.status_code}")
        except Exception as e:
            duration = time.time() - start_time
            response_times.append(duration)
            print(f"Request {i+1} Error:", e)
    print_stats("REST User Login", response_times)

def rest_admin_login():
    print("\n--- REST Admin Login ---")
    response_times = []
    payload = {"username": "admin", "password": "admin123"}
    for i in range(NUM_REQUESTS):
        start_time = time.time()
        try:
            res = requests.post(f"{BASE_URL}/adminlogin", json=payload)
            duration = time.time() - start_time
            response_times.append(duration)
            print(f"Request {i+1}: {res.status_code}")
        except Exception as e:
            duration = time.time() - start_time
            response_times.append(duration)
            print(f"Request {i+1} Error:", e)
    print_stats("REST Admin Login", response_times)

def rest_inventory():
    print("\n--- REST Inventory ---")
    response_times = []
    for i in range(NUM_REQUESTS):
        start_time = time.time()
        try:
            res = requests.get(f"{BASE_URL}/api/inventory/all")
            duration = time.time() - start_time
            response_times.append(duration)
            print(f"Request {i+1}: {res.status_code}")
        except Exception as e:
            duration = time.time() - start_time
            response_times.append(duration)
            print(f"Request {i+1} Error:", e)
    print_stats("REST Inventory", response_times)

def rest_analytics():
    print("\n--- REST Analytics ---")
    response_times = []
    for i in range(NUM_REQUESTS):
        start_time = time.time()
        try:
            res = requests.get(f"{BASE_URL}/analytics?month=12&year=2025")
            duration = time.time() - start_time
            response_times.append(duration)
            print(f"Request {i+1}: {res.status_code}")
        except Exception as e:
            duration = time.time() - start_time
            response_times.append(duration)
            print(f"Request {i+1} Error:", e)
    print_stats("REST Analytics", response_times)

# ----------------------
# gRPC REQUEST FUNCTIONS
# ----------------------
def grpc_create_order(stub):
    req = order_pb2.CreateOrderRequest()
    req.cafe_id = str(TEST_CAFE_ID)
    item = req.items.add()
    item.item_id = str(TEST_ITEM_ID)
    item.quantity = 1
    item.price = TEST_ITEM_PRICE
    return stub.CreateOrder(req)

def grpc_login(stub):
    req = login_pb2.LoginRequest(cafe_id=TEST_CAFE_ID, access_code=TEST_USER_ACCESS)
    return stub.AuthenticateCafe(req)

def grpc_admin(stub):
    req = adminlogin_pb2.LoginRequest(username="admin", password="admin123")
    return stub.Login(req)

def grpc_cafe(stub):
    req = cafe_pb2.CafeCreateRequest(
        nom="PerfTest Cafe",
        localisation="Test Loc",
        code_acces=random_string()
    )
    return stub.CreateCafe(req)

def grpc_inventory(stub):
    req = inventory_pb2.UpdateInventoryRequest(
        item_id="",
        cafe_id=str(TEST_CAFE_ID),
        quantity_ordered=0
    )
    return stub.GetInventoryByCafe(req)

def grpc_menu(stub):
    req = menu_pb2.MenuItemRequest(name="Perf Menu Item", category="Food", price=5.0)
    return stub.AddMenuItem(req)

def grpc_restock_item(stub, item_id, cafe_id, quantity):
    req = inventory_pb2.RestockItemRequest(
        item_id=str(item_id),
        cafe_id=str(cafe_id),
        quantity_added=quantity,
        restock_date=datetime.now().isoformat()
    )
    return stub.RestockItem(req)

# ----------------------
# gRPC TEST FUNCTIONS
# ----------------------
def test_grpc_service(stub_class, service_name, request_func, address):
    print(f"\n--- gRPC {service_name} ---")
    channel = grpc.insecure_channel(address)
    stub = stub_class(channel)
    response_times = []
    for i in range(NUM_REQUESTS):
        start_time = time.time()
        try:
            response = request_func(stub)
            duration = time.time() - start_time
            response_times.append(duration)
            print(f"Request {i+1}: Success")
        except grpc.RpcError as e:
            duration = time.time() - start_time
            response_times.append(duration)
            print(f"Request {i+1}: {e.code()} - {e.details()}")
    channel.close()
    print_stats(f"gRPC {service_name}", response_times)

def test_grpc_order_service_with_restock(order_stub, inventory_stub):
    print("\n--- gRPC Order with Auto-Restock ---")
    response_times = []
    for i in range(NUM_REQUESTS):
        # Restock 1 unit before each order
        grpc_restock_item(inventory_stub, TEST_ITEM_ID, TEST_CAFE_ID, 1)

        # Create order
        start_time = time.time()
        try:
            response = grpc_create_order(order_stub)
            duration = time.time() - start_time
            response_times.append(duration)
            print(f"Request {i+1}: Success")
        except grpc.RpcError as e:
            duration = time.time() - start_time
            response_times.append(duration)
            print(f"Request {i+1}: {e.code()} - {e.details()}")
    print_stats("gRPC Order with Auto-Restock", response_times)

# ----------------------
# MAIN
# ----------------------
if __name__ == "__main__":
    print("Starting Performance Tests...")

    # ---------------- REST Tests ----------------
    rest_orders()
    rest_user_login()
    rest_admin_login()
    rest_inventory()
    rest_analytics()

    # ---------------- gRPC Tests ----------------
    order_channel = grpc.insecure_channel(GRPC_ADDRESSES["order"])
    order_stub = order_pb2_grpc.OrderServiceStub(order_channel)

    inventory_channel = grpc.insecure_channel(GRPC_ADDRESSES["inventory"])
    inventory_stub = inventory_pb2_grpc.InventoryServiceStub(inventory_channel)

    # Test order with auto-restock
    test_grpc_order_service_with_restock(order_stub, inventory_stub)

    # Other gRPC services
    test_grpc_service(login_pb2_grpc.LoginServiceStub, "login", grpc_login, GRPC_ADDRESSES["login"])
    test_grpc_service(adminlogin_pb2_grpc.AdminLoginServiceStub, "admin", grpc_admin, GRPC_ADDRESSES["admin"])
    test_grpc_service(cafe_pb2_grpc.CafeServiceStub, "cafe", grpc_cafe, GRPC_ADDRESSES["cafe"])
    test_grpc_service(inventory_pb2_grpc.InventoryServiceStub, "inventory", grpc_inventory, GRPC_ADDRESSES["inventory"])
    test_grpc_service(menu_pb2_grpc.MenuServiceStub, "menu", grpc_menu, GRPC_ADDRESSES["menu"])

    # Close channels
    order_channel.close()
    inventory_channel.close()

    print("\nPerformance Tests Completed!")
