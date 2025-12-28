# tests/test_cafe_service.py
import pytest
import grpc
import requests
from shared_proto import cafe_pb2, cafe_pb2_grpc
import random
import string

# ---------------- Fixtures ----------------
@pytest.fixture
def grpc_stub():
    """Create a gRPC stub connected to the running cafe service"""
    channel = grpc.insecure_channel("localhost:5004")
    stub = cafe_pb2_grpc.CafeServiceStub(channel)
    yield stub
    channel.close()


@pytest.fixture
def base_url():
    """Base URL for REST API integration tests"""
    return "http://localhost:5000/api/cafes"


# ---------------- Helper ----------------
def unique_code(length=5):
    """Generate a random unique access code"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))


# ---------------- Unit Tests (gRPC) ----------------
def test_create_cafe_grpc(grpc_stub):
    code = unique_code()
    request = cafe_pb2.CafeCreateRequest(
        nom="Test Cafe",
        localisation="Test Location",
        code_acces=code
    )
    response = grpc_stub.CreateCafe(request)
    assert response.success
    assert response.nom == "Test Cafe"
    assert response.code_acces == code


def test_get_all_cafes_grpc(grpc_stub):
    response = grpc_stub.GetAllCafes(cafe_pb2.Empty())
    # Instead of isinstance(list), check if it behaves like a sequence
    assert len(response.cafes) >= 0  # There is a collection
    for cafe in response.cafes:
        assert hasattr(cafe, "id")
        assert hasattr(cafe, "nom")
        assert hasattr(cafe, "localisation")
        assert hasattr(cafe, "code_acces")


def test_update_cafe_grpc(grpc_stub):
    # First create a cafe
    code = unique_code()
    create_resp = grpc_stub.CreateCafe(
        cafe_pb2.CafeCreateRequest(nom="Update Cafe", localisation="Loc", code_acces=code)
    )
    cafe_id = create_resp.id

    update_resp = grpc_stub.UpdateCafe(
        cafe_pb2.CafeUpdateRequest(id=cafe_id, nom="Updated Cafe", localisation="New Loc", code_acces=code)
    )
    assert update_resp.success
    assert update_resp.nom == "Updated Cafe"


def test_delete_cafe_grpc(grpc_stub):
    code = unique_code()
    create_resp = grpc_stub.CreateCafe(
        cafe_pb2.CafeCreateRequest(nom="Delete Cafe", localisation="Loc", code_acces=code)
    )
    cafe_id = create_resp.id

    delete_resp = grpc_stub.DeleteCafe(cafe_pb2.CafeDeleteRequest(id=cafe_id))
    assert delete_resp.success


def test_verify_cafe_code_grpc(grpc_stub):
    code = unique_code()
    create_resp = grpc_stub.CreateCafe(
        cafe_pb2.CafeCreateRequest(nom="Verify Cafe", localisation="Loc", code_acces=code)
    )

    verify_resp = grpc_stub.VerifyCafeCode(cafe_pb2.CafeVerifyCodeRequest(code_acces=code))
    assert verify_resp.success
    assert verify_resp.cafe_id == create_resp.id


# ---------------- Integration Tests (REST API) ----------------
def test_create_cafe_rest(base_url):
    code = unique_code()
    data = {
        "name": "REST Cafe",
        "location": "REST Location",
        "access_code": code
    }
    resp = requests.post(base_url, json=data)
    json_data = resp.json()
    assert resp.status_code == 200
    assert json_data["success"]
    assert json_data["cafe"]["access_code"] == code


def test_get_all_cafes_rest(base_url):
    resp = requests.get(base_url)
    json_data = resp.json()
    assert resp.status_code == 200
    assert json_data["success"]
    assert isinstance(json_data["cafes"], list)


def test_update_cafe_rest(base_url):
    # Create first
    code = unique_code()
    data = {"name": "REST Update", "location": "Loc", "access_code": code}
    create_resp = requests.post(base_url, json=data).json()
    cafe_id = create_resp["cafe"]["id"]

    # Update
    update_data = {"name": "REST Updated", "location": "New Loc", "access_code": code}
    resp = requests.put(f"{base_url}/{cafe_id}", json=update_data)
    json_data = resp.json()
    assert resp.status_code == 200
    assert json_data["success"]
    assert json_data["cafe"]["name"] == "REST Updated"


def test_delete_cafe_rest(base_url):
    # Create first
    code = unique_code()
    data = {"name": "REST Delete", "location": "Loc", "access_code": code}
    create_resp = requests.post(base_url, json=data).json()
    cafe_id = create_resp["cafe"]["id"]

    # Delete
    resp = requests.delete(f"{base_url}/{cafe_id}")
    json_data = resp.json()
    assert resp.status_code == 200
    assert json_data["success"]


def test_verify_cafe_code_rest(base_url):
    # Create first
    code = unique_code()
    data = {"name": "REST Verify", "location": "Loc", "access_code": code}
    create_resp = requests.post(base_url, json=data).json()
    cafe_id = create_resp["cafe"]["id"]

    # Verify
    resp = requests.post(f"{base_url}/verify-code", json={"access_code": code})
    json_data = resp.json()
    assert resp.status_code == 200
    assert json_data["valid"]
    assert json_data["cafe"]["id"] == cafe_id
