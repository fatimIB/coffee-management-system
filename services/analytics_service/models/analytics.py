from database.db_connection import get_connection

class Analytics:
    def __init__(self):
        self.conn = get_connection()
        if not self.conn:
            raise Exception("Database connection not available")
    
    def query(self, sql, params=None):
        if not self.conn:
            return None
        cursor = self.conn.cursor(dictionary=True)
        cursor.execute(sql, params or ())
        result = cursor.fetchall()
        cursor.close()
        return result

    def top_product_this_month(self, month, year):
        sql = """
            SELECT m.name, SUM(oi.quantity) AS total
            FROM order_items oi
            JOIN menu_items m ON oi.item_id = m.item_id
            JOIN orders o ON oi.order_id = o.order_id
            WHERE MONTH(o.created_at)=%s AND YEAR(o.created_at)=%s
            GROUP BY m.name
            ORDER BY total DESC
            LIMIT 1
        """
        result = self.query(sql, (month, year))
        return result[0] if result else None

    def top_cafe_this_month(self, month, year):
        sql = """
            SELECT c.name, SUM(o.total_price) AS total
            FROM orders o
            JOIN cafes c ON o.cafe_id = c.cafe_id
            WHERE MONTH(o.created_at)=%s AND YEAR(o.created_at)=%s
            GROUP BY c.name
            ORDER BY total DESC
            LIMIT 1
        """
        result = self.query(sql, (month, year))
        return result[0] if result else None

    def total_sales_this_month(self, month, year):
        sql = """
            SELECT SUM(total_price) AS total_sales
            FROM orders
            WHERE MONTH(created_at)=%s AND YEAR(created_at)=%s
        """
        result = self.query(sql, (month, year))
        if result and result[0]['total_sales'] is not None:
            return result[0]
        return {"total_sales": 0}  # default to 0

    def growth_rate_vs_last_month(self, month, year):
        current = self.total_sales_this_month(month, year)['total_sales'] or 0
        last_month = self.total_sales_this_month(
            month - 1 if month > 1 else 12,
            year if month > 1 else year - 1
        )['total_sales'] or 0
    
        if last_month == 0:
            return 0
        return round((current - last_month) / last_month * 100, 2)
    

    def cafe_comparison(self, month, year):
        sql = """
            SELECT c.name AS cafe, SUM(o.total_price) AS total_sales
            FROM orders o
            JOIN cafes c ON o.cafe_id = c.cafe_id
            WHERE MONTH(o.created_at)=%s AND YEAR(o.created_at)=%s
            GROUP BY c.name
            ORDER BY total_sales DESC
        """
        return self.query(sql, (month, year))


    def sales_over_time(self, month, year):
        sql = """
            SELECT c.name AS cafe, DATE(o.created_at) AS date, SUM(o.total_price) AS daily_total
            FROM orders o
            JOIN cafes c ON o.cafe_id = c.cafe_id
            WHERE MONTH(o.created_at)=%s AND YEAR(o.created_at)=%s
            GROUP BY c.name, DATE(o.created_at)
            ORDER BY DATE(o.created_at)
        """
        return self.query(sql, (month, year))


    def products_overview(self, month, year):
        sql = """
            SELECT c.name AS cafe, m.name AS product, SUM(oi.quantity) AS qty
            FROM order_items oi
            JOIN menu_items m ON oi.item_id = m.item_id
            JOIN orders o ON oi.order_id = o.order_id
            JOIN cafes c ON o.cafe_id = c.cafe_id
            WHERE MONTH(o.created_at)=%s AND YEAR(o.created_at)=%s
            GROUP BY c.name, m.name
            ORDER BY qty DESC
        """
        rows = self.query(sql, (month, year))
    
        cafes = {}
        for r in rows:
            cafe = r["cafe"]
            if cafe not in cafes:
                cafes[cafe] = []
            cafes[cafe].append({
                "product": r["product"],
                "qty": int(r["qty"])  # <-- cast Decimal to int
            })
    
        result = {}
        for cafe, items in cafes.items():
            result[cafe] = {
                "top_3": items[:3],
                "bottom_3": items[-3:]
            }
    
        return result
    
    def category_distribution(self, month, year):
        sql = """
            SELECT m.category, SUM(oi.quantity * m.price) AS total
            FROM order_items oi
            JOIN menu_items m ON oi.item_id = m.item_id
            JOIN orders o ON oi.order_id = o.order_id
            WHERE MONTH(o.created_at)=%s AND YEAR(o.created_at)=%s
            GROUP BY m.category
        """
        rows = self.query(sql, (month, year))
    
        # Convert Decimal to float
        for row in rows:
            row['total'] = float(row['total']) if row['total'] is not None else 0.0
    
        return rows
    