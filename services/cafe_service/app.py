# services/cafe_service/app.py
from database.db_connection import get_connection
import grpc
from concurrent import futures
import time
from shared_proto import cafe_pb2, cafe_pb2_grpc

class CafeService(cafe_pb2_grpc.CafeServiceServicer):

    def _get_inserted_id(self, cursor, access_code):
        """Robust method to get inserted ID"""
        try:
            row = cursor.fetchone()
            if row is not None:
                return row[0]
        except Exception:
            pass

        try:
            return getattr(cursor, "lastrowid", None)
        except Exception:
            pass

        try:
            cursor.execute("SELECT cafe_id FROM cafes WHERE access_code=%s", (access_code,))
            row = cursor.fetchone()
            return row[0] if row else None
        except Exception:
            return None

    # -------------------- CREATE --------------------
    def CreateCafe(self, request, context):
        conn = get_connection()
        if conn is None:
            context.set_code(grpc.StatusCode.UNAVAILABLE)
            context.set_details("Database unavailable")
            return cafe_pb2.CafeResponse(success=False)

        cursor = conn.cursor()
        try:
            try:
                cursor.execute(
                    "INSERT INTO cafes (name, location, access_code) VALUES (%s, %s, %s) RETURNING cafe_id;",
                    (request.nom, request.localisation, request.code_acces)
                )
            except Exception:
                cursor.execute(
                    "INSERT INTO cafes (name, location, access_code) VALUES (%s, %s, %s)",
                    (request.nom, request.localisation, request.code_acces)
                )

            cafe_id = self._get_inserted_id(cursor, request.code_acces)
            conn.commit()

            if cafe_id is None:
                return cafe_pb2.CafeResponse(
                    id=0,
                    nom=request.nom,
                    localisation=request.localisation,
                    code_acces=request.code_acces,
                    success=True,
                    message="Café créé (id non récupéré)"
                )

            return cafe_pb2.CafeResponse(
                id=cafe_id,
                nom=request.nom,
                localisation=request.localisation,
                code_acces=request.code_acces,
                success=True,
                message="Café créé avec succès"
            )

        except Exception as e:
            conn.rollback()
            msg = str(e).lower()
            if "duplicate" in msg or "unique" in msg or "already exists" in msg:
                context.set_code(grpc.StatusCode.ALREADY_EXISTS)
                context.set_details("Code d'accès déjà existant")
                return cafe_pb2.CafeResponse(success=False, message="Code d'accès déjà existant")
            else:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(str(e))
                return cafe_pb2.CafeResponse(success=False, message="Erreur base de données")

        finally:
            cursor.close()
            conn.close()

    # -------------------- GET ALL --------------------
    def GetAllCafes(self, request, context):
        conn = get_connection()
        if conn is None:
            context.set_code(grpc.StatusCode.UNAVAILABLE)
            context.set_details("Database unavailable")
            return cafe_pb2.CafeListResponse()

        cursor = conn.cursor()
        try:
            cursor.execute("SELECT cafe_id, name, location, access_code FROM cafes")
            rows = cursor.fetchall()
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return cafe_pb2.CafeListResponse()
        finally:
            cursor.close()
            conn.close()

        cafes = [
            cafe_pb2.Cafe(
                id=row[0],
                nom=row[1],
                localisation=row[2],
                code_acces=row[3]
            )
            for row in rows
        ]

        return cafe_pb2.CafeListResponse(cafes=cafes)

    # -------------------- UPDATE --------------------
    def UpdateCafe(self, request, context):
        conn = get_connection()
        if conn is None:
            context.set_code(grpc.StatusCode.UNAVAILABLE)
            context.set_details("Database unavailable")
            return cafe_pb2.CafeResponse(success=False)

        cursor = conn.cursor()
        try:
            cursor.execute(
                "UPDATE cafes SET name=%s, location=%s, access_code=%s WHERE cafe_id=%s",
                (request.nom, request.localisation, request.code_acces, request.id)
            )
            conn.commit()
            updated = cursor.rowcount
        except Exception as e:
            conn.rollback()
            msg = str(e).lower()
            if "duplicate" in msg or "unique" in msg or "already exists" in msg:
                context.set_code(grpc.StatusCode.ALREADY_EXISTS)
                context.set_details("Code d'accès déjà existant")
                return cafe_pb2.CafeResponse(success=False, message="Code d'accès déjà existant")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return cafe_pb2.CafeResponse(success=False, message="Erreur base de données")
        finally:
            cursor.close()
            conn.close()

        if updated == 0:
            return cafe_pb2.CafeResponse(success=False, message="Café non trouvé")

        return cafe_pb2.CafeResponse(
            id=request.id,
            nom=request.nom,
            localisation=request.localisation,
            code_acces=request.code_acces,
            success=True,
            message="Café mis à jour"
        )

    # -------------------- DELETE --------------------
    def DeleteCafe(self, request, context):
        conn = get_connection()
        if conn is None:
            context.set_code(grpc.StatusCode.UNAVAILABLE)
            context.set_details("Database unavailable")
            return cafe_pb2.CafeResponse(success=False)

        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM cafes WHERE cafe_id=%s", (request.id,))
            conn.commit()
            deleted = cursor.rowcount
        except Exception as e:
            conn.rollback()
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return cafe_pb2.CafeResponse(success=False, message="Erreur base de données")
        finally:
            cursor.close()
            conn.close()

        if deleted == 0:
            return cafe_pb2.CafeResponse(success=False, message="Café non trouvé")

        return cafe_pb2.CafeResponse(success=True, message="Café supprimé")

    # -------------------- VERIFY --------------------
    def VerifyCafeCode(self, request, context):
        conn = get_connection()
        if conn is None:
            context.set_code(grpc.StatusCode.UNAVAILABLE)
            context.set_details("Database unavailable")
            return cafe_pb2.CafeVerifyCodeResponse(success=False)

        cursor = conn.cursor()
        try:
            cursor.execute("SELECT cafe_id, name, location FROM cafes WHERE access_code=%s", (request.code_acces,))
            row = cursor.fetchone()
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return cafe_pb2.CafeVerifyCodeResponse(success=False, message="Erreur base de données")
        finally:
            cursor.close()
            conn.close()

        if not row:
            return cafe_pb2.CafeVerifyCodeResponse(success=False, cafe_id=0, message="Code invalide")

        return cafe_pb2.CafeVerifyCodeResponse(
            success=True,
            cafe_id=row[0],
            nom=row[1],
            localisation=row[2],
            message="Code vérifié"
        )

# -------------------- SERVER --------------------
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    cafe_pb2_grpc.add_CafeServiceServicer_to_server(CafeService(), server)
    server.add_insecure_port('[::]:5004')
    server.start()
    print("Cafe service running on port 5004...")
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    serve()
