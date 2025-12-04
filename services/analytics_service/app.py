from concurrent import futures
import grpc
from shared_proto import analytics_pb2, analytics_pb2_grpc
from models.analytics import Analytics
from models.predictions import SalesPredictor

class AnalyticsServiceServicer(analytics_pb2_grpc.AnalyticsServiceServicer):
    def __init__(self):
        self.analytics = Analytics()
        self.predictor = SalesPredictor()

    def GetCardMetrics(self, request, context):
        month, year = request.month, request.year
        top_product_data = self.analytics.top_product_this_month(month, year)
        top_cafe_data = self.analytics.top_cafe_this_month(month, year)
        total_sales_data = self.analytics.total_sales_this_month(month, year)
        growth = self.analytics.growth_rate_vs_last_month(month, year)

        return analytics_pb2.CardMetrics(
            top_product=top_product_data['name'] if top_product_data else '',
            top_cafe=top_cafe_data['name'] if top_cafe_data else '',
            total_sales=float(total_sales_data['total_sales'] if total_sales_data else 0),
            growth_percent=growth
        )
    
    def GetOverviewAnalytics(self, request, context):
        month, year = request.month, request.year

        cafe_cmp = self.analytics.cafe_comparison(month, year)
        over_time = self.analytics.sales_over_time(month, year)
        products = self.analytics.products_overview(month, year)
        categories = self.analytics.category_distribution(month, year)

        response = analytics_pb2.OverviewAnalytics()

        # Café comparison
        for row in cafe_cmp:
            response.cafe_comparison.add(
                cafe=row["cafe"],
                total_sales=row["total_sales"]
            )

        # Sales over time
        for row in over_time:
            response.sales_overtime.add(
                cafe=row["cafe"],
                date=str(row["date"]),
                daily_total=row["daily_total"]
            )

        
        # Top 3 & bottom 3 products
        for cafe, info in products.items():
            cafe_entry = response.products_overview.add(cafe=cafe)
        
            for item in info["top_3"]:
                cafe_entry.top_3.add(product=item["product"], qty=item["qty"])  # qty is already int
        
            for item in info["bottom_3"]:
                cafe_entry.bottom_3.add(product=item["product"], qty=item["qty"])  # qty is int
        
        # Category distribution
        for row in categories:
            response.category_distribution.add(
                category=row["category"],
                total=row["total"]  # already float
            )

        return response
    
    def GetPredictions(self, request, context):
       df_pred = self.predictor.predict_next_month_sales()
       if df_pred is None:
           return analytics_pb2.PredictionResponse(predictions=[])
       predictions = [
           analytics_pb2.CafePrediction(
               cafe_name=row["cafe_name"],
               current_sales=row["current_sales"],
               predicted_sales=row["predicted_sales"],
               growth_percent=row["growth_percent"],
               rank=row["rank"]
           ) for _, row in df_pred.iterrows()
       ]
       return analytics_pb2.PredictionResponse(predictions=predictions)



   


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    analytics_pb2_grpc.add_AnalyticsServiceServicer_to_server(AnalyticsServiceServicer(), server)
    server.add_insecure_port('[::]:5003')
    print("Analytics gRPC server running on port 5003...")
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
