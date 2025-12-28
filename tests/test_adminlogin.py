import pytest
import grpc
import requests
from shared_proto import adminlogin_pb2, adminlogin_pb2_grpc

# ----------------------------
# gRPC Admin Login Unit Tests
# ----------------------------
@pytest.fixture
def grpc_stub():
    """Create a gRPC stub connected to the running admin login service"""
    channel = grpc.insecure_channel("localhost:50011")
    stub = adminlogin_pb2_grpc.AdminLoginServiceStub(channel)
    yield stub
    channel.close()


def test_admin_login_success(grpc_stub):
    """Test a successful login with valid credentials"""
    # Replace with credentials you know exist in your DB
    request = adminlogin_pb2.LoginRequest(username="admin", password="admin123")
    response = grpc_stub.Login(request)
    assert response.success is True
    assert response.admin_id > 0
    assert "Login successful" in response.message


def test_admin_login_failure(grpc_stub):
    """Test login failure with invalid credentials"""
    request = adminlogin_pb2.LoginRequest(username="wrong", password="wrong")
    response = grpc_stub.Login(request)
    assert response.success is False
    assert response.admin_id == 0
    assert "Invalid credentials" in response.message


def test_update_admin_info(grpc_stub):
    """Test updating admin username and password"""
    # Replace admin_id with a valid ID from your DB
    admin_id = 1
    request = adminlogin_pb2.UpdateAdminRequest(admin_id=admin_id, username="admin", password="admin123")
    response = grpc_stub.UpdateAdminInfo(request)
    assert response.success is True
    assert "updated successfully" in response.message

# ----------------------------
# REST API Integration Tests
# ----------------------------
BASE_URL = "http://localhost:5000"

def test_admin_login_rest():
    """Test admin login via gateway REST endpoint"""
    url = f"{BASE_URL}/adminlogin"
    payload = {"username": "admin", "password": "admin123"}
    response = requests.post(url, json=payload)
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert "admin_id" in json_data


def test_admin_session_check_rest():
    url_login = f"{BASE_URL}/adminlogin"
    payload = {"username": "admin", "password": "admin123"}
    with requests.Session() as s:
        login_res = s.post(url_login, json=payload)
        assert login_res.status_code == 200
        json_data = login_res.json()
        assert json_data["success"] is True

        url_check = f"{BASE_URL}/api/admin/session"
        check_res = s.get(url_check)
        assert check_res.status_code == 200
        json_data = check_res.json()
        assert json_data["authenticated"] is True
        assert "admin_id" in json_data

