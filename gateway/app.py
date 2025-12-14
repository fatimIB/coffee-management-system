from flask import Flask, jsonify, request
from grpc_clients import analytics_client, inventory_client
from flask_cors import CORS  # import CORS
from collections import defaultdict
import math
from grpc_clients.menu_client import get_menu_items, add_menu_item, update_menu_item, delete_menu_item
from grpc_clients.order_client import create_order, get_orders_by_cafe
from dotenv import load_dotenv
from database.db_connection import get_connection

# Load env variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable


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

# -------- LOGIN API --------
@app.route('/api/login', methods=['POST'])
def api_login():
    try:
        data = request.json
        if not data or 'access_code' not in data:
            return jsonify({"success": False, "message": "Missing access_code"}), 400
        
        access_code = data['access_code']
        conn = get_connection()
        if not conn:
            return jsonify({"success": False, "message": "Database connection failed"}), 500
        
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT cafe_id, name, location FROM cafes WHERE access_code = %s",
            (access_code,)
        )
        cafe = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if cafe:
            return jsonify({
                "success": True,
                "cafe_id": cafe['cafe_id'],
                "cafe_name": cafe['name'],
                "location": cafe['location']
            })
        else:
            return jsonify({"success": False, "message": "Invalid access code"}), 401
            
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
