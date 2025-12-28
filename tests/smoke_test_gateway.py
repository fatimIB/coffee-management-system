import requests

GATEWAY_URL = "http://127.0.0.1:5000"

def test_orders_route():
    try:
        resp = requests.get(f"{GATEWAY_URL}/orders/1")  # Example cafe_id = 1
        print("Orders route:", resp.status_code, resp.json())
    except Exception as e:
        print("Orders route error:", e)

def test_menu_route():
    try:
        resp = requests.get(f"{GATEWAY_URL}/menu/items")
        print("Menu route:", resp.status_code, resp.json())
    except Exception as e:
        print("Menu route error:", e)

def test_session_route():
    try:
        resp = requests.get(f"{GATEWAY_URL}/api/session")
        print("Session route:", resp.status_code, resp.json())
    except Exception as e:
        print("Session route error:", e)

if __name__ == "__main__":
    test_orders_route()
    test_menu_route()
    test_session_route()
