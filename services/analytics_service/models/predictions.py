from database.db_connection import get_connection
import pandas as pd
from sklearn.linear_model import LinearRegression
from datetime import datetime


class SalesPredictor:
    def __init__(self):
        self.conn = get_connection()

    # -------------------------------
    # Monthly sales per café
    # -------------------------------
    def get_monthly_sales_per_cafe(self):
        """Fetch total monthly sales for each cafe from orders table."""
        query = """
            SELECT 
                c.name AS cafe_name,
                YEAR(o.created_at) AS year,
                MONTH(o.created_at) AS month,
                SUM(o.total_price) AS total_sales
            FROM orders o
            JOIN cafes c ON o.cafe_id = c.cafe_id
            GROUP BY c.name, YEAR(o.created_at), MONTH(o.created_at)
            ORDER BY c.name, year, month;
        """
        df = pd.read_sql(query, self.conn)
        return df

    # -------------------------------
    # Predict next month's sales
    # -------------------------------
    def predict_next_month_sales(self):
        """Predict next month's sales for each cafe and rank them."""
        df = self.get_monthly_sales_per_cafe()
        if df.empty:
            print("No sales data found.")
            return None

        predictions = []

        for cafe in df['cafe_name'].unique():
            cafe_data = df[df['cafe_name'] == cafe].copy()
            cafe_data['time_index'] = (
                cafe_data['year'] - df['year'].min()) * 12 + cafe_data['month']

            X = cafe_data[['time_index']]
            y = cafe_data['total_sales']

            if len(X) < 2:
                # Not enough historical data → use last month's sales as prediction
                predicted_sales = float(y.iloc[-1])
                current_sales = predicted_sales
                growth = 0
            else:
                model = LinearRegression()
                model.fit(X, y)
                next_time_index = cafe_data['time_index'].max() + 1
                predicted_sales = float(model.predict([[next_time_index]])[0])
                current_sales = y.iloc[-1]
                growth = ((predicted_sales - current_sales) / current_sales) * 100 if current_sales else 0

            predictions.append({
                "cafe_name": cafe,
                "current_sales": round(current_sales, 2),
                "predicted_sales": round(predicted_sales, 2),
                "growth_percent": round(growth, 2)
            })

        df_pred = pd.DataFrame(predictions)
        df_pred = df_pred.sort_values(by="predicted_sales", ascending=False).reset_index(drop=True)
        df_pred['rank'] = df_pred.index + 1
        return df_pred

    # -------------------------------
    # Best-selling item per café
    # -------------------------------
    def best_selling_item_per_cafe(self):
        """Show which menu item sells the most per café."""
        query = """
            SELECT
                c.name AS cafe_name,
                i.name AS item_name,
                SUM(a.quantity) AS total_sold
            FROM analytics_logs a
            JOIN cafes c ON a.cafe_id = c.cafe_id
            JOIN menu_items i ON a.item_id = i.item_id
            GROUP BY c.name, i.name
            ORDER BY c.name, total_sold DESC;
        """
        df = pd.read_sql(query, self.conn)
        return df

    # -------------------------------
    # Display everything
    # -------------------------------
    def show_predictions(self):
        # Sales prediction + ranking
        df_pred = self.predict_next_month_sales()
        if df_pred is None or df_pred.empty:
            print("No predictions to display.")
            return

        print("\n📊 Next Month’s Sales per Café (Predicted)\n")
        print(df_pred[['cafe_name', 'current_sales', 'predicted_sales', 'growth_percent']].to_string(index=False))

        print("\n🏆 Café Performance Prediction Ranking\n")
        print(df_pred[['rank', 'cafe_name', 'predicted_sales', 'growth_percent']].to_string(index=False))

        # Best-selling items
        try:
            df_items = self.best_selling_item_per_cafe()
            print("\n☕ Best-Selling Item per Café\n")
            for cafe in df_items['cafe_name'].unique():
                top_item = df_items[df_items['cafe_name'] == cafe].iloc[0]
                print(f"{cafe}: {top_item['item_name']} (Sold: {top_item['total_sold']})")
        except Exception as e:
            print("⚠ Could not fetch best-selling items. Make sure analytics_logs exists.")
            print("Error:", e)


if __name__ == "__main__":
    predictor = SalesPredictor()
    predictor.show_predictions()
