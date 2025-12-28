from database.db_connection import get_connection

import grpc
from concurrent import futures
import time

from shared_proto import login_pb2, login_pb2_grpc

class LoginServicer(login_pb2_grpc.LoginServiceServicer):
    
    def AuthenticateCafe(self, request, context):
        """Authentifier un café avec son ID et code d'accès"""
        conn = get_connection()
        if conn is None:
            context.set_code(grpc.StatusCode.UNAVAILABLE)
            context.set_details('Database connection failed')
            return login_pb2.LoginResponse(
                success=False,
                message="Erreur de connexion à la base de données",
                cafe_id=0,
                cafe_name=""
            )
        
        try:
            cursor = conn.cursor()
            
            # Requête pour vérifier le café et son code
            query = """
                SELECT cafe_id, name, location 
                FROM cafes 
                WHERE cafe_id = %s AND access_code = %s
            """
            cursor.execute(query, (request.cafe_id, request.access_code))
            result = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            if result:
                # Authentification réussie
                print(f"✅ Authentification réussie pour {result[1]} (ID: {result[0]})")
                return login_pb2.LoginResponse(
                    success=True,
                    message="Connexion réussie",
                    cafe_id=result[0],
                    cafe_name=result[1]
                )
            else:
                # Échec de l'authentification
                print(f"❌ Échec authentification - Café ID: {request.cafe_id}")
                return login_pb2.LoginResponse(
                    success=False,
                    message="Code d'accès incorrect",
                    cafe_id=0,
                    cafe_name=""
                )
                
        except Exception as e:
            print(f"❌ Erreur lors de l'authentification: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f'Erreur serveur: {str(e)}')
            return login_pb2.LoginResponse(
                success=False,
                message="Erreur serveur",
                cafe_id=0,
                cafe_name=""
            )
    
    def GetAllCafes(self, request, context):
        """Récupérer la liste de tous les cafés pour le dropdown"""
        conn = get_connection()
        if conn is None:
            context.set_code(grpc.StatusCode.UNAVAILABLE)
            context.set_details('Database connection failed')
            return login_pb2.CafeListResponse(cafes=[])
        
        try:
            cursor = conn.cursor()
            
            # Récupérer tous les cafés
            query = "SELECT cafe_id, name, location FROM cafes ORDER BY name"
            cursor.execute(query)
            results = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            # Créer la liste des cafés
            cafes = []
            for row in results:
                cafe = login_pb2.Cafe(
                    id=row[0],  # cafe_id
                    name=row[1],
                    location=row[2]
                )
                cafes.append(cafe)
            
            print(f"✅ {len(cafes)} cafés récupérés")
            return login_pb2.CafeListResponse(cafes=cafes)
            
        except Exception as e:
            print(f"❌ Erreur lors de la récupération des cafés: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f'Erreur serveur: {str(e)}')
            return login_pb2.CafeListResponse(cafes=[])

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    login_pb2_grpc.add_LoginServiceServicer_to_server(LoginServicer(), server)
    server.add_insecure_port('[::]:5001')
    server.start()
    print("🔐 Login service running on port 5001...")
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    serve()