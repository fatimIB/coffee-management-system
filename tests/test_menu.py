import pytest
import grpc
import requests
from shared_proto import menu_pb2, menu_pb2_grpc

# ----------------------------
# gRPC Menu Unit Tests
# ----------------------------
@pytest.fixture(scope="module")
def grpc_stub():
    """Create a gRPC stub connected to the running MenuService."""
    channel = grpc.insecure_channel("localhost:5005")  # gRPC server port
    stub = menu_pb2_grpc.MenuServiceStub(channel)
    yield stub
    channel.close()

def create_test_menu_item(stub, name="Test Item", category="Food", price=10.0):
    """Helper to create a menu item via gRPC."""
    request = menu_pb2.MenuItemRequest(name=name, category=category, price=price)
    response = stub.AddMenuItem(request)
    return response

def test_add_menu_item(grpc_stub):
    response = create_test_menu_item(grpc_stub)
    assert response.id > 0
    assert response.name == "Test Item"
    assert response.category == "Food"
    assert response.price == 10.0

def test_update_menu_item(grpc_stub):
    item = create_test_menu_item(grpc_stub, name="Update Test")
    request = menu_pb2.MenuItemRequest(
        id=item.id,
        name="Updated Test",
        category=item.category,
        price=18.0
    )
    response = grpc_stub.UpdateMenuItem(request)
    assert response.name == "Updated Test"
    assert response.price == 18.0

def test_delete_menu_item(grpc_stub):
    item = create_test_menu_item(grpc_stub, name="Delete Test")
    request = menu_pb2.MenuItemRequest(id=item.id)
    response = grpc_stub.DeleteMenuItem(request)
    assert response.success is True

# ----------------------------
# REST API Menu Tests
# ----------------------------
rest_base_url = "http://localhost:5000/api/menu"  # gateway URL

def create_rest_menu_item(name="REST Test Item", category="Drink", price=11.0):
    payload = {"name": name, "category": category, "price": price}
    res = requests.post(f"{rest_base_url}/add", json=payload)
    res.raise_for_status()
    return res.json()

def test_add_menu_item_rest():
    data = create_rest_menu_item()
    assert data.get("id") is not None
    assert data.get("name") == "REST Test Item"
    assert data.get("category") == "Drink"
    assert data.get("price") == pytest.approx(11.0)

def test_update_menu_item_rest():
    # Create first
    item = create_rest_menu_item(name="Update REST", category="Food", price=13.0)
    menu_id = item.get("id")
    # Update
    update_payload = {"id": menu_id, "name": "Updated REST", "category": "Food", "price": 15.0}
    res = requests.put(f"{rest_base_url}/update", json=update_payload)
    res.raise_for_status()
    updated_item = res.json()
    assert updated_item.get("name") == "Updated REST"
    assert updated_item.get("price") == pytest.approx(15.0)

def test_delete_menu_item_rest():
    # Create first
    item = create_rest_menu_item(name="Delete REST", category="Food", price=10.0)
    menu_id = item.get("id")
    # Delete
    res = requests.delete(f"{rest_base_url}/delete", json={"id": menu_id})
    res.raise_for_status()
    result = res.json()
    assert result.get("success") is True
