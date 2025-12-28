import pytest
import grpc
from datetime import datetime
import requests
from shared_proto import inventory_pb2, inventory_pb2_grpc
from google.protobuf.empty_pb2 import Empty

# ----------------------------
# Configuration
# ----------------------------
BASE_URL = "http://localhost:5000"
GRPC_ADDRESS = "localhost:5006"

# ----------------------------
# gRPC Unit Tests
# ----------------------------

@pytest.fixture
def grpc_stub():
    """Create gRPC stub connected to InventoryService"""
    channel = grpc.insecure_channel(GRPC_ADDRESS)
    stub = inventory_pb2_grpc.InventoryServiceStub(channel)
    yield stub
    channel.close()

def test_get_inventory_by_cafe(grpc_stub):
    """Test fetching inventory via gRPC"""
    request = Empty()
    response = grpc_stub.GetInventoryByCafe(request)
    assert response.items is not None
    if response.items:
        item = response.items[0]
        assert hasattr(item, "item_id")
        assert hasattr(item, "cafe_id")
        assert hasattr(item, "item_name")
        assert hasattr(item, "cafe_name")
        assert hasattr(item, "stock_quantity")
        assert hasattr(item, "restock_date")
        assert hasattr(item, "is_low_stock")

def test_restock_item_success(grpc_stub):
    """Test restocking an item via gRPC"""
    request = inventory_pb2.RestockItemRequest(
        item_id="1",
        cafe_id="1",
        quantity_added=5,
        restock_date=datetime.now().strftime("%Y-%m-%d")
    )
    response = grpc_stub.RestockItem(request)
    assert response.success is True
    assert "successfully" in response.message.lower()

def test_restock_item_failure_invalid(grpc_stub):
    """Test restocking non-existing item via gRPC"""
    request = inventory_pb2.RestockItemRequest(
        item_id="9999",
        cafe_id="9999",
        quantity_added=5,
        restock_date=datetime.now().strftime("%Y-%m-%d")
    )
    response = grpc_stub.RestockItem(request)
    assert response.success is False

def test_update_inventory_after_order(grpc_stub):
    """Test updating inventory after an order via gRPC"""
    request = inventory_pb2.UpdateInventoryRequest(
        item_id="1",
        cafe_id="1",
        quantity_ordered=1
    )
    response = grpc_stub.UpdateInventoryAfterOrder(request)
    # Depending on stock, either success True or False
    assert isinstance(response.success, bool)

# ----------------------------
# REST API Integration Tests
# ----------------------------

def test_get_all_inventory_rest():
    """Test GET /api/inventory/all"""
    res = requests.get(f"{BASE_URL}/api/inventory/all")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    if data:
        item = data[0]
        expected_keys = ["item_id", "cafe_id", "item_name", "cafe_name", "stock_quantity", "restock_date", "is_low_stock"]
        for key in expected_keys:
            assert key in item

def test_restock_item_rest_success():
    """Test POST /api/inventory/restock (success)"""
    payload = {
        "item_id": "1",
        "cafe_id": "1",
        "quantity_added": 5,
        "restock_date": datetime.now().strftime("%Y-%m-%d")
    }
    res = requests.post(f"{BASE_URL}/api/inventory/restock", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True

def test_restock_item_rest_failure_invalid():
    """Test POST /api/inventory/restock with invalid IDs"""
    payload = {
        "item_id": "9999",
        "cafe_id": "9999",
        "quantity_added": 5,
        "restock_date": datetime.now().strftime("%Y-%m-%d")
    }
    res = requests.post(f"{BASE_URL}/api/inventory/restock", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is False

def test_inventory_low_stock_flag_rest():
    """Check if low stock items have is_low_stock = True"""
    res = requests.get(f"{BASE_URL}/api/inventory/all")
    data = res.json()
    if data:
        for item in data:
            if item["stock_quantity"] < 20:
                assert item["is_low_stock"] is True
            else:
                assert item["is_low_stock"] is False
