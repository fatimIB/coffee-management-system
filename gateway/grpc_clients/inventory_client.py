import os
import grpc
from shared_proto  import inventory_pb2, inventory_pb2_grpc

# Adresse du Service Inventaire
# - En production / via docker-compose: "inventory_service:5006"
# - En développement local (services lancés sur la machine): "localhost:5006"
INVENTORY_SERVICE_ADDRESS = os.getenv("INVENTORY_SERVICE_ADDRESS", "inventory_service:5006")

class InventoryClient:
    def __init__(self):
        # Création du canal de communication non sécurisé
        self.channel = grpc.insecure_channel(INVENTORY_SERVICE_ADDRESS)
        self.stub = inventory_pb2_grpc.InventoryServiceStub(self.channel)

    def get_all_inventory(self):
        try:
            response = self.stub.GetInventoryByCafe(inventory_pb2.Empty())
            # Convertir la réponse répétée (liste d'objets) en liste de dictionnaires pour le Flask/JSON
            return [
                {
                    "item_id": item.item_id,
                    "cafe_id": item.cafe_id,
                    "item_name": item.item_name,
                    "cafe_name": item.cafe_name,
                    "stock_quantity": item.stock_quantity,
                    "restock_date": item.restock_date,
                    "is_low_stock": item.is_low_stock
                } for item in response.items
            ]
        except grpc.RpcError as e:
            print(f"Erreur gRPC lors de l'appel à l'inventaire: {e.details()}")
            return []

    def restock_item(self, item_id, cafe_id, quantity_added, date):
        request = inventory_pb2.RestockItemRequest(
            item_id=item_id,
            cafe_id=cafe_id,
            quantity_added=quantity_added,
            restock_date=date
        )
        try:
            response = self.stub.RestockItem(request)
            return {"success": response.success, "message": response.message}
        except grpc.RpcError as e:
            print(f"Erreur gRPC RestockItem: {e.details()}")
            return {"success": False, "message": f"Erreur de communication: {e.details()}"}

    # Cette méthode serait utilisée par le Service Commandes (via la Gateway si vous la centralisez)
    def update_inventory(self, item_id, cafe_id, quantity_ordered):
        request = inventory_pb2.UpdateInventoryRequest(
            item_id=item_id,
            cafe_id=cafe_id,
            quantity_ordered=quantity_ordered
        )
        try:
            response = self.stub.UpdateInventoryAfterOrder(request)
            return response.success
        except grpc.RpcError as e:
            print(f"Erreur gRPC UpdateInventoryAfterOrder: {e.details()}")
            return False