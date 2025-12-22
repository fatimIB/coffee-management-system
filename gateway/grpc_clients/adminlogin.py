import grpc
from shared_proto import adminlogin_pb2, adminlogin_pb2_grpc

class AdminLoginClient:
    def __init__(self, host="adminlogin", port=50011):
        self.channel = grpc.insecure_channel(f"{host}:{port}")
        self.stub = adminlogin_pb2_grpc.AdminLoginServiceStub(self.channel)

    def login(self, username, password):
        request = adminlogin_pb2.LoginRequest(username=username, password=password)
        response = self.stub.Login(request)
        return {
            "success": response.success,
            "message": response.message,
            "admin_id": response.admin_id
        }
    
    def update_admin_info(self, admin_id, username=None, password=None):
        request = adminlogin_pb2.UpdateAdminRequest(
            admin_id=admin_id,
            username=username or "",
            password=password or ""
        )
        response = self.stub.UpdateAdminInfo(request)
        return {"success": response.success, "message": response.message}

