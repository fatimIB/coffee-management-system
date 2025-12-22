import grpc
import os
import sys

# Ajouter shared_proto au path
sys.path.append('/app/shared_proto')
from shared_proto import login_pb2, login_pb2_grpc

class LoginClient:
    def __init__(self):
        # Connexion au service gRPC
        self.host = os.getenv('LOGIN_SERVICE_HOST', 'login_service')
        self.port = os.getenv('LOGIN_SERVICE_PORT', '50052')
        self.channel = grpc.insecure_channel(f'{self.host}:{self.port}')
        self.stub = login_pb2_grpc.LoginServiceStub(self.channel)

        try:
            grpc.channel_ready_future(self.channel).result(timeout=5)
            print("✅ Connected to login_service gRPC")
        except grpc.FutureTimeoutError:
            print("❌ login_service gRPC not ready")
    
    def authenticate_cafe(self, cafe_id, access_code):
        """
        Authentifier un café
        
        Args:
            cafe_id (int): ID du café
            access_code (str): Code d'accès
            
        Returns:
            dict: {'success': bool, 'message': str, 'cafe_id': int, 'cafe_name': str}
        """
        try:
            request = login_pb2.LoginRequest(
                cafe_id=cafe_id,
                access_code=access_code
            )
            response = self.stub.AuthenticateCafe(
                request,
                timeout=5,
                wait_for_ready=True
            )
            
            return {
                'success': response.success,
                'message': response.message,
                'cafe_id': response.cafe_id,
                'cafe_name': response.cafe_name
            }
        except grpc.RpcError as e:
            #print(f"Erreur gRPC: {e}")
            print("❌ LoginService gRPC unreachable")
            print(e.details())
            print(e.code())
            return {
                'success': False,
                'message': 'Erreur de connexion au service',
                'cafe_id': 0,
                'cafe_name': ''
            }
    
    def get_all_cafes(self):
        """
        Récupérer tous les cafés pour le dropdown
        
        Returns:
            list: [{'id': int, 'name': str, 'location': str}, ...]
        """
        try:
            request = login_pb2.EmptyRequest()
            response = self.stub.GetAllCafes(
                request,
                timeout=5,
                wait_for_ready=True
            )
            
            cafes = []
            for cafe in response.cafes:
                cafes.append({
                    'id': cafe.id,
                    'name': cafe.name,
                    'location': cafe.location
                })
            
            return cafes
        except grpc.RpcError as e:
            #print(f"Erreur gRPC: {e}")
            print("❌ LoginService gRPC unreachable")
            print(e.details())
            print(e.code())
            return []
    
    def close(self):
        """Fermer la connexion"""
        self.channel.close()