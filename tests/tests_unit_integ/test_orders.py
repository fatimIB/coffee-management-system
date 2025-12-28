import pytest
import grpc
import requests
from shared_proto import order_pb2, order_pb2_grpc

# ============================
# CONFIG
# ============================
GRPC_ORDER_PORT = "localhost:5002"
REST_BASE_URL = "http://localhost:5000"

TEST_CAFE_ID = "1"     
TEST_ITEM_ID = "1"     
TEST_ITEM_PRICE = 10.0


# ============================
# gRPC FIXTURE
# ============================
@pytest.fixture(scope="module")
def grpc_stub():
    channel = grpc.insecure_channel(GRPC_ORDER_PORT)
    stub = order_pb2_grpc.OrderServiceStub(channel)
    yield stub
    channel.close()


# ============================
# gRPC HELPERS
# ============================
def create_test_order_grpc(stub):
    request = order_pb2.CreateOrderRequest(cafe_id=TEST_CAFE_ID)

    item = request.items.add()
    item.item_id = TEST_ITEM_ID
    item.quantity = 1
    item.price = TEST_ITEM_PRICE

    return stub.CreateOrder(request)


# ============================
# gRPC TESTS (UNIT)
# ============================
def test_create_order_grpc(grpc_stub):
    response = create_test_order_grpc(grpc_stub)

    assert response.success is True
    assert response.order_id is not None
    assert response.total_price == pytest.approx(TEST_ITEM_PRICE)


def test_get_orders_by_cafe_grpc(grpc_stub):
    request = order_pb2.GetOrdersRequest(cafe_id=TEST_CAFE_ID)
    response = grpc_stub.GetOrdersByCafe(request)

    assert len(response.orders) >= 1

    order = response.orders[0]
    assert order.cafe_id == TEST_CAFE_ID
    assert order.total_price > 0
    assert len(order.items) >= 1


# ============================
# REST HELPERS
# ============================
def create_test_order_rest():
    payload = {
        "cafe_id": TEST_CAFE_ID,
        "items": [
            {
                "item_id": TEST_ITEM_ID,
                "quantity": 1,
                "price": TEST_ITEM_PRICE
            }
        ]
    }

    res = requests.post(f"{REST_BASE_URL}/orders/create", json=payload)
    res.raise_for_status()
    return res.json()


# ============================
# REST TESTS (INTEGRATION)
# ============================
def test_create_order_rest():
    data = create_test_order_rest()

    assert data["success"] is True
    assert data["order_id"] is not None
    assert data["total_price"] == pytest.approx(TEST_ITEM_PRICE)


def test_get_orders_by_cafe_rest():
    res = requests.get(f"{REST_BASE_URL}/orders/{TEST_CAFE_ID}")
    res.raise_for_status()
    data = res.json()

    assert "orders" in data
    assert len(data["orders"]) >= 1

    order = data["orders"][0]
    assert order["cafe_id"] == TEST_CAFE_ID
    assert order["total_price"] > 0
    assert len(order["items"]) >= 1
