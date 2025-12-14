# grpc_clients/cafe_client.py
import grpc
from shared_proto import cafe_pb2, cafe_pb2_grpc

CAFE_SERVICE_HOST = "cafe_service:5004"  # Nom du service dans docker-compose

def get_all_cafes():
    """
    Récupère tous les cafés depuis le service café via gRPC
    """
    with grpc.insecure_channel(CAFE_SERVICE_HOST) as channel:
        stub = cafe_pb2_grpc.CafeServiceStub(channel)
        response = stub.GetAllCafes(cafe_pb2.Empty())
        return response  # response.cafes

def create_cafe(name: str, location: str, access_code: str):
    """
    Crée un nouveau café
    """
    with grpc.insecure_channel(CAFE_SERVICE_HOST) as channel:
        stub = cafe_pb2_grpc.CafeServiceStub(channel)
        request = cafe_pb2.CafeCreateRequest(
            nom=name,
            localisation=location,
            code_acces=access_code
        )
        response = stub.CreateCafe(request)
        return response

def update_cafe(cafe_id: int, name: str, location: str, access_code: str):
    """
    Met à jour un café existant
    """
    with grpc.insecure_channel(CAFE_SERVICE_HOST) as channel:
        stub = cafe_pb2_grpc.CafeServiceStub(channel)
        request = cafe_pb2.CafeUpdateRequest(
            id=cafe_id,
            nom=name,
            localisation=location,
            code_acces=access_code
        )
        response = stub.UpdateCafe(request)
        return response

def delete_cafe(cafe_id: int):
    """
    Supprime un café
    """
    with grpc.insecure_channel(CAFE_SERVICE_HOST) as channel:
        stub = cafe_pb2_grpc.CafeServiceStub(channel)
        request = cafe_pb2.CafeDeleteRequest(id=cafe_id)
        response = stub.DeleteCafe(request)
        return response

def verify_cafe_code(access_code: str):
    """
    Vérifie si le code d'accès d'un café est valide
    """
    with grpc.insecure_channel(CAFE_SERVICE_HOST) as channel:
        stub = cafe_pb2_grpc.CafeServiceStub(channel)
        request = cafe_pb2.CafeVerifyCodeRequest(code_acces=access_code)
        response = stub.VerifyCafeCode(request)
        return response
