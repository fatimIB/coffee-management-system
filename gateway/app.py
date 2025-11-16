from flask import Flask, jsonify, request
from grpc_clients import analytics_client
from flask_cors import CORS  # import CORS
from collections import defaultdict
import math

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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
