from flask import Flask, jsonify, request, session, redirect
from grpc_clients import analytics_client, inventory_client, cafe_client
from grpc_clients.adminlogin import AdminLoginClient
from grpc_clients.login_client import LoginClient
from flask_cors import CORS  # import CORS
from collections import defaultdict
import bcrypt
import math
from grpc_clients.menu_client import get_menu_items, add_menu_item, update_menu_item, delete_menu_item
from grpc_clients.order_client import create_order, get_orders_by_cafe
from database.db_connection import get_connection
from dotenv import load_dotenv
import os

# Load env variables
load_dotenv()



app = Flask(__name__)
CORS(
    app,
    supports_credentials=True,
    origins=[
        "http://localhost:8080",
        "http://127.0.0.1:8080"
    ] 
) 

app.secret_key = os.getenv('SECRET_KEY')
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="None",  
    SESSION_COOKIE_SECURE=True     
)
login_client = LoginClient()
admin_client = AdminLoginClient() 

# --- Admin login ---
@app.route("/adminlogin", methods=["POST"])
def adminlogin():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"success": False, "message": "Username and password required"}), 400

    try:
        # Call gRPC service
        result = admin_client.login(username, password)
        if result["success"]:
            session["admin_id"] = result["admin_id"]
            session["username"] = username
            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "message": result.get("message", "Invalid credentials")}), 401
    except Exception as e:
        return jsonify({"success": False, "message": f"Server error: {str(e)}"}), 500

# --- Dashboard route ---
@app.route("/dashboard/index.html")
def dashboard():
    if "admin_id" not in session:
        return redirect("/adminlogin/index.html")
    return app.send_static_file("dashboard/index.html")

# --- Logout route ---
@app.route("/adminlogout", methods=["POST"])
def admin_logout():
    session.clear()
    return jsonify({
        "success": True,
        "message": "Logged out successfully"
    }), 200


@app.route("/api/admin/session", methods=["GET"])
def check_admin_session():
    if "admin_id" in session:
        return jsonify({
            "authenticated": True,
            "admin_id": session.get("admin_id"),
            "username": session.get("username")
        }), 200

    return jsonify({
        "authenticated": False
    }), 401


@app.route("/api/admin/update", methods=["POST"])
def update_admin():
    if "admin_id" not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401

    data = request.json
    username = data.get("username")
    password = data.get("password")

    try:
        result = admin_client.update_admin_info(
            admin_id=session["admin_id"],
            username=username,
            password=password
        )
        if result["success"]:
            if username:
                session["username"] = username  # update session
            return jsonify({"success": True, "message": result["message"]})
        return jsonify(result), 400
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


# --- Analytics servivce ---

@app.route('/analytics', methods=['GET'])
def get_analytics():
    month = int(request.args.get('month', 10))
    year = int(request.args.get('year', 2025))
    
    try:
        response = analytics_client.get_card_metrics(month, year)
        return jsonify({
            "top_product": response.top_product,
            "top_cafe": response.top_cafe,
            "total_sales": response.total_sales,
            "growth_percent": response.growth_percent
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/analytics/overview', methods=['GET'])
def get_overview():
    month = int(request.args.get('month', 10))
    year = int(request.args.get('year', 2025))

    try:
        resp = analytics_client.get_overview_analytics(month, year)

        # Basic lists from gRPC
        cafe_comparison = [
            {"cafe": c.cafe, "total_sales": float(c.total_sales)}
            for c in resp.cafe_comparison
        ]

        # sales_overtime is a flat list of (cafe, date, daily_total)
        sales_overtime_flat = [
            {"cafe": s.cafe, "date": s.date, "daily_total": float(s.daily_total)}
            for s in resp.sales_overtime
        ]

        # Build sales_per_cafe_daily: grouped by cafe with ordered dates/totals
        grouped = defaultdict(list)
        for row in sales_overtime_flat:
            grouped[row["cafe"]].append((row["date"], row["daily_total"]))

        sales_per_cafe_daily = []
        # For consistent ordering: collect global date set and sort
        all_dates = sorted({r["date"] for r in sales_overtime_flat})
        for cafe, rows in grouped.items():
            # make a dict date->total, fill zeros for missing dates
            date_map = {d: t for d, t in rows}
            totals = [date_map.get(d, 0.0) for d in all_dates]
            sales_per_cafe_daily.append({
                "cafe": cafe,
                "dates": all_dates,
                "totals": [float(round(t, 2)) if not math.isnan(t) else 0.0 for t in totals]
            })

        # Products overview (list of cafe objects with top_3 and bottom_3)
        products_overview = []
        top_products_per_cafe = []
        least_products_per_cafe = []
        for p in resp.products_overview:
            top_list = [{"product": t.product, "qty": int(t.qty)} for t in p.top_3]
            bottom_list = [{"product": b.product, "qty": int(b.qty)} for b in p.bottom_3]
            products_overview.append({
                "cafe": p.cafe,
                "top_3": top_list,
                "bottom_3": bottom_list
            })
            # top single and least single (if available)
            if top_list:
                top_products_per_cafe.append({
                    "cafe": p.cafe,
                    "product": top_list[0]["product"],
                    "qty": int(top_list[0]["qty"])
                })
            if bottom_list:
                least_products_per_cafe.append({
                    "cafe": p.cafe,
                    "product": bottom_list[0]["product"],
                    "qty": int(bottom_list[0]["qty"])
                })

        # Category distribution
        category_distribution = [
            {"category": c.category, "total": float(c.total)}
            for c in resp.category_distribution
        ]

        return jsonify({
            "cafe_comparison": cafe_comparison,
            "sales_overtime": sales_overtime_flat,
            "sales_per_cafe_daily": sales_per_cafe_daily,
            "products_overview": products_overview,
            "top_products_per_cafe": top_products_per_cafe,
            "least_products_per_cafe": least_products_per_cafe,
            "category_distribution": category_distribution
        })


    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/analytics/predictions', methods=['GET'])
def get_predictions():
    try:
        resp = analytics_client.get_predictions()
        predictions = [
            {
                "cafe_name": p.cafe_name,
                "current_sales": p.current_sales,
                "predicted_sales": p.predicted_sales,
                "growth_percent": p.growth_percent,
                "rank": p.rank
            } for p in resp.predictions
        ]
        return jsonify(predictions)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -------- MENU API --------
@app.route("/api/menu", methods=["GET"])
def api_get_menu():
    try:
        search = request.args.get("search", "")
        items = get_menu_items(search)
        return jsonify(items)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/menu/add", methods=["POST"])
def api_add_menu():
    try:
        data = request.json
        if not data or not all(k in data for k in ["name", "category", "price"]):
            return jsonify({"error": "Missing required fields"}), 400
        item = add_menu_item(data["name"], data["category"], float(data["price"]))
        if item is None:
            return jsonify({"error": "Failed to add menu item"}), 500
        return jsonify(item)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/menu/update", methods=["PUT"])
def api_update_menu():
    try:
        data = request.json
        if not data or not all(k in data for k in ["id", "name", "category", "price"]):
            return jsonify({"error": "Missing required fields"}), 400
        item = update_menu_item(data["id"], data["name"], data["category"], float(data["price"]))
        if item is None:
            return jsonify({"error": "Failed to update menu item"}), 500
        return jsonify(item)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/menu/delete", methods=["DELETE"])
def api_delete_menu():
    try:
        data = request.json
        if not data or "id" not in data:
            return jsonify({"error": "Missing id field"}), 400
        success = delete_menu_item(data["id"])
        return jsonify({"success": success})
    except Exception as e:
        return jsonify({"error": str(e)}), 500



# Add these new routes for inventory
@app.route('/api/inventory/all', methods=['GET'])
def get_all_inventory():
    try:
        client = inventory_client.InventoryClient()
        items = client.get_all_inventory()
        return jsonify(items)
    except Exception as e:
        print(f"Error getting inventory: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/inventory/restock', methods=['POST'])
def restock_item():
    try:
        data = request.json
        client = inventory_client.InventoryClient()
        result = client.restock_item(
            item_id=data.get('item_id'),
            cafe_id=data.get('cafe_id'),
            quantity_added=data.get('quantity_added'),
            date=data.get('restock_date')
        )
        return jsonify(result)
    except Exception as e:
        print(f"Error restocking item: {e}")
        return jsonify({"error": str(e)}), 500



# --------------------- CAFES ---------------------
@app.route('/api/cafes', methods=['GET'])
def get_all_cafes():
    try:
        response = cafe_client.get_all_cafes()
        cafes = [{
            'id': c.id,
            'name': c.nom,
            'location': c.localisation,
            'access_code': c.code_acces
        } for c in response.cafes]
        return jsonify({'success': True, 'cafes': cafes})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/cafes', methods=['POST'])
def create_cafe():
    try:
        data = request.get_json()
        response = cafe_client.create_cafe(
            data['name'],
            data['location'],
            data['access_code']
        )
        if response.success:
            return jsonify({
                'success': True,
                'message': response.message,
                'cafe': {
                    'id': response.id,
                    'name': response.nom,
                    'location': response.localisation,
                    'access_code': response.code_acces
                }
            })
        else:
            return jsonify({'success': False, 'error': response.message}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/cafes/<int:cafe_id>', methods=['PUT'])
def update_cafe(cafe_id):
    try:
        data = request.get_json()
        response = cafe_client.update_cafe(
            cafe_id,
            data['name'],
            data['location'],
            data['access_code']
        )
        if response.success:
            return jsonify({
                'success': True,
                'message': response.message,
                'cafe': {
                    'id': response.id,
                    'name': response.nom,
                    'location': response.localisation,
                    'access_code': response.code_acces
                }
            })
        else:
            return jsonify({'success': False, 'error': response.message}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/cafes/<int:cafe_id>', methods=['DELETE'])
def delete_cafe(cafe_id):
    try:
        response = cafe_client.delete_cafe(cafe_id)
        if response.success:
            return jsonify({'success': True, 'message': response.message})
        else:
            return jsonify({'success': False, 'error': response.message}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/cafes/verify-code', methods=['POST'])
def verify_cafe_code():
    try:
        data = request.get_json()
        response = cafe_client.verify_cafe_code(data['access_code'])
        return jsonify({
            'valid': response.success,
            'message': response.message,
            'cafe': {
                'id': response.cafe_id,
                'name': getattr(response, 'nom', ''),
                'location': getattr(response, 'localisation', ''),
                'access_code': data['access_code']
            } if response.success else None
        })
    except Exception as e:
        return jsonify({'valid': False, 'error': str(e)}), 500


# -------- ORDER API --------
@app.route('/orders/create', methods=['POST'])
def api_create_order():
    try:
        data = request.json
        if not data or 'cafe_id' not in data or 'items' not in data:
            return jsonify({"success": False, "message": "Missing cafe_id or items"}), 400
        
        result = create_order(data['cafe_id'], data['items'])
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/orders/<cafe_id>', methods=['GET'])
def api_get_orders(cafe_id):
    try:
        orders = get_orders_by_cafe(cafe_id)
        return jsonify({"orders": orders})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -------- MENU API (for orders page) --------
@app.route('/menu/items', methods=['GET'])
def api_menu_items():
    try:
        items = get_menu_items()
        return jsonify({"items": items})
    except Exception as e:
        return jsonify({"error": str(e)}), 500



# Routes for Login
@app.route('/api/login/cafes', methods=['GET'])
def get_cafes():
    """Récupérer la liste des cafés pour le dropdown"""
    try:
        cafes = login_client.get_all_cafes()
        return jsonify({
            'success': True,
            'cafes': cafes
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erreur: {str(e)}'
        }), 500

@app.route('/api/login', methods=['POST'])
def login():
    """Authentifier un café"""
    try:
        data = request.get_json()
        cafe_id = data.get('cafe_id')
        access_code = data.get('access_code')
        
        if not cafe_id or not access_code:
            return jsonify({
                'success': False,
                'message': 'Café et code requis'
            }), 400
        
        result = login_client.authenticate_cafe(
            cafe_id=int(cafe_id),
            access_code=access_code
        )
        
        if result['success']:
            session['cafe_id'] = result['cafe_id']
            session['cafe_name'] = result['cafe_name']
            session['is_authenticated'] = True
        
        return jsonify(result), 200 if result['success'] else 401
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erreur: {str(e)}'
        }), 500

@app.route('/api/userlogout', methods=['POST'])
def user_logout():
    """Déconnexion"""
    session.clear()
    return jsonify({
        'success': True,
        'message': 'Déconnexion réussie'
    }), 200

@app.route('/api/session', methods=['GET'])
def get_session():
    """Vérifier si l'utilisateur est connecté"""
    if session.get('is_authenticated'):
        return jsonify({
            'authenticated': True,
            'cafe_id': session.get('cafe_id'),
            'cafe_name': session.get('cafe_name')
        }), 200
    else:
        return jsonify({
            'authenticated': False
        }), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
