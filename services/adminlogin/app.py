import grpc
from concurrent import futures
import time
from shared_proto import adminlogin_pb2, adminlogin_pb2_grpc
from database.db_connection import get_connection
import bcrypt

class AdminLoginServicer(adminlogin_pb2_grpc.AdminLoginServiceServicer):
    def Login(self, request, context):
        """Authenticate admin using username and password"""
        conn = get_connection()
        if conn is None:
            context.set_code(grpc.StatusCode.UNAVAILABLE)
            context.set_details('Database connection failed')
            return adminlogin_pb2.LoginResponse(
                success=False,
                message="Database connection failed",
                admin_id=0
            )

        try:
            cursor = conn.cursor()
            query = "SELECT admin_id, password_hash FROM admins WHERE username=%s"
            cursor.execute(query, (request.username,))
            result = cursor.fetchone()
            cursor.close()
            conn.close()

            if result:
                admin_id, password_hash = result
                if bcrypt.checkpw(request.password.encode(), password_hash.encode()):
                    return adminlogin_pb2.LoginResponse(
                        success=True,
                        message="Login successful",
                        admin_id=admin_id
                    )

            return adminlogin_pb2.LoginResponse(
                success=False,
                message="Invalid credentials",
                admin_id=0
            )

        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Server error: {e}")
            return adminlogin_pb2.LoginResponse(success=False, message="Server error", admin_id=0)
    
    def UpdateAdminInfo(self, request, context):
        conn = get_connection()
        if conn is None:
            context.set_code(grpc.StatusCode.UNAVAILABLE)
            context.set_details("Database connection failed")
            return adminlogin_pb2.UpdateAdminResponse(success=False, message="Database connection failed")
    
        try:
            cursor = conn.cursor()
            if request.username:
                cursor.execute("UPDATE admins SET username=%s WHERE admin_id=%s", (request.username, request.admin_id))
            if request.password:
                hashed = bcrypt.hashpw(request.password.encode(), bcrypt.gensalt())
                cursor.execute("UPDATE admins SET password_hash=%s WHERE admin_id=%s", (hashed.decode(), request.admin_id))
            conn.commit()
            cursor.close()
            conn.close()
            return adminlogin_pb2.UpdateAdminResponse(success=True, message="Admin info updated successfully")
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Server error: {e}")
            return adminlogin_pb2.UpdateAdminResponse(success=False, message="Server error")


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    adminlogin_pb2_grpc.add_AdminLoginServiceServicer_to_server(AdminLoginServicer(), server)
    server.add_insecure_port('[::]:50011')
    server.start()
    print("🔐 AdminLogin gRPC service running on port 50011...")
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == "__main__":
    serve()
