import grpc
from proto import analytics_pb2, analytics_pb2_grpc

channel = grpc.insecure_channel('analytics_service:5003')
stub = analytics_pb2_grpc.AnalyticsServiceStub(channel)

def get_card_metrics(month, year):
    request = analytics_pb2.MonthRequest(month=month, year=year)
    return stub.GetCardMetrics(request)

def get_overview_analytics(month, year):
    request = analytics_pb2.MonthRequest(month=month, year=year)
    return stub.GetOverviewAnalytics(request)

def get_predictions():
    request = analytics_pb2.PredictionRequest()
    return stub.GetPredictions(request)
