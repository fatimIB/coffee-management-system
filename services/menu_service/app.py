from database.db_connection import get_connection  

import grpc
from concurrent import futures
import time

from shared_proto import menu_pb2, menu_pb2_grpc

class MenuService(menu_pb2_grpc.MenuServiceServicer):
    def AddMenuItem(self, request, context):
        conn = get_connection()
        if conn is None:
            context.set_code(grpc.StatusCode.UNAVAILABLE)
            context.set_details("Database connection failed")
            return menu_pb2.MenuItemResponse(id=0, name="", category="", price=0.0)
        
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO menu_items (name, category, price) VALUES (%s, %s, %s)",
            (request.name, request.category, request.price)
        )
        conn.commit()
        item_id = cursor.lastrowid
        cursor.close()
        conn.close()
        return menu_pb2.MenuItemResponse(
            id=item_id,
            name=request.name,
            category=request.category,
            price=request.price
        )

    def GetMenuItems(self, request, context):
        conn = get_connection()
        if conn is None:
            context.set_code(grpc.StatusCode.UNAVAILABLE)
            context.set_details("Database connection failed")
            return menu_pb2.MenuItemsResponse(items=[])
        
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM menu_items")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        items = [
            menu_pb2.MenuItemResponse(
                id=row[0],  # item_id
                name=row[1],  # name
                category=row[2],  # category
                price=float(row[3])  # price
            ) for row in rows
        ]
        return menu_pb2.MenuItemsResponse(items=items)

    def UpdateMenuItem(self, request, context):
        conn = get_connection()
        if conn is None:
            context.set_code(grpc.StatusCode.UNAVAILABLE)
            context.set_details("Database connection failed")
            return menu_pb2.MenuItemResponse(id=0, name="", category="", price=0.0)
        
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE menu_items SET name=%s, category=%s, price=%s WHERE item_id=%s",
            (request.name, request.category, request.price, request.id)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return menu_pb2.MenuItemResponse(
            id=request.id,
            name=request.name,
            category=request.category,
            price=request.price
        )

    def DeleteMenuItem(self, request, context):
        conn = get_connection()
        if conn is None:
            context.set_code(grpc.StatusCode.UNAVAILABLE)
            context.set_details("Database connection failed")
            return menu_pb2.DeleteResponse(success=False)
        
        cursor = conn.cursor()
        cursor.execute("DELETE FROM menu_items WHERE item_id=%s", (request.id,))
        conn.commit()
        affected = cursor.rowcount
        cursor.close()
        conn.close()
        return menu_pb2.DeleteResponse(success=affected > 0)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    menu_pb2_grpc.add_MenuServiceServicer_to_server(MenuService(), server)
    server.add_insecure_port('[::]:5005')
    server.start()
    print("Menu service running on port 5005...")
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':
    serve()
