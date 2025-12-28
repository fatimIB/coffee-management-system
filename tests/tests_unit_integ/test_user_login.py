import pytest
import grpc
import requests
from shared_proto import login_pb2, login_pb2_grpc
from google.protobuf.empty_pb2 import Empty

BASE_URL = "http://localhost:5000"

# ----------------------------
# gRPC Unit Tests
# ----------------------------
@pytest.fixture
def grpc_stub():
    """Create a gRPC stub connected to the running login service"""
    channel = grpc.insecure_channel("localhost:5001")
    stub = login_pb2_grpc.LoginServiceStub(channel)
    yield stub
    channel.close()

def test_authenticate_cafe_success(grpc_stub):
    """Test successful cafe login"""
    request = login_pb2.LoginRequest(cafe_id=1, access_code="DK456")
    response = grpc_stub.AuthenticateCafe(request)
    assert response.success is True
    assert response.cafe_id > 0
    assert response.cafe_name != ""

def test_authenticate_cafe_failure(grpc_stub):
    """Test login failure with wrong access code"""
    request = login_pb2.LoginRequest(cafe_id=1, access_code="wrong")
    response = grpc_stub.AuthenticateCafe(request)
    assert response.success is False
    assert response.cafe_id == 0
    assert response.cafe_name == ""

def test_get_all_cafes(grpc_stub):
    """Test getting the list of all cafes"""
    request = Empty() 
    response = grpc_stub.GetAllCafes(request)
    assert len(response.cafes) > 0
    assert all(hasattr(cafe, "id") and hasattr(cafe, "name") for cafe in response.cafes)

# ----------------------------
# REST API Integration Tests
# ----------------------------
def test_login_rest_success():
    """Test login via REST API"""
    payload = {"cafe_id": 1, "access_code": "DK456"}
    res = requests.post(f"{BASE_URL}/api/login", json=payload, allow_redirects=False)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert "cafe_id" in data

def test_login_rest_failure():
    """Test REST login with wrong access code"""
    payload = {"cafe_id": 1, "access_code": "wrong"}
    res = requests.post(f"{BASE_URL}/api/login", json=payload, allow_redirects=False)
    assert res.status_code == 401
    data = res.json()
    assert data["success"] is False

def test_get_cafes_rest():
    """Test getting cafes for dropdown"""
    res = requests.get(f"{BASE_URL}/api/login/cafes")
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert isinstance(data["cafes"], list)
    assert len(data["cafes"]) > 0

def test_session_rest():
    """Test session persistence after login"""
    payload = {"cafe_id": 1, "access_code": "DK456"}
    with requests.Session() as s:
        login_res = s.post(f"{BASE_URL}/api/login", json=payload)
        assert login_res.status_code == 200
        data = login_res.json()
        assert data["success"] is True

        session_res = s.get(f"{BASE_URL}/api/session")
        assert session_res.status_code == 200
        session_data = session_res.json()
        assert session_data["authenticated"] is True
        assert "cafe_id" in session_data

def test_user_logout_rest():
    """Test logging out clears session"""
    payload = {"cafe_id": 1, "access_code": "DK456"}
    with requests.Session() as s:
        login_res = s.post(f"{BASE_URL}/api/login", json=payload)
        logout_res = s.post(f"{BASE_URL}/api/userlogout")
        assert logout_res.status_code == 200
        logout_data = logout_res.json()
        assert logout_data["success"] is True

        session_res = s.get(f"{BASE_URL}/api/session")
        session_data = session_res.json()
        assert session_data["authenticated"] is False
