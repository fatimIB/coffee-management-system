import requests

BASE_URL = "http://localhost:5000"

# ----------------------------
# Analytics / Overview Tests
# ----------------------------

def test_get_analytics_overview():
    """Test the overview analytics endpoint"""
    res = requests.get(f"{BASE_URL}/analytics/overview?month=10&year=2025")
    assert res.status_code == 200

    data = res.json()
    # Check main keys exist
    expected_keys = [
        "cafe_comparison",
        "sales_overtime",
        "sales_per_cafe_daily",
        "products_overview",
        "top_products_per_cafe",
        "least_products_per_cafe",
        "category_distribution"
    ]
    for key in expected_keys:
        assert key in data

    # Basic type checks
    assert isinstance(data["cafe_comparison"], list)
    assert isinstance(data["sales_overtime"], list)
    assert isinstance(data["sales_per_cafe_daily"], list)
    assert isinstance(data["products_overview"], list)
    assert isinstance(data["top_products_per_cafe"], list)
    assert isinstance(data["least_products_per_cafe"], list)
    assert isinstance(data["category_distribution"], list)

# ----------------------------
# Analytics Card Metrics
# ----------------------------

def test_get_analytics_card_metrics():
    """Test the main card metrics endpoint"""
    res = requests.get(f"{BASE_URL}/analytics?month=10&year=2025")
    assert res.status_code == 200

    data = res.json()
    expected_keys = ["top_product", "top_cafe", "total_sales", "growth_percent"]
    for key in expected_keys:
        assert key in data

    # Check types
    assert isinstance(data["top_product"], str)
    assert isinstance(data["top_cafe"], str)
    assert isinstance(data["total_sales"], (int, float))
    assert isinstance(data["growth_percent"], (int, float))

# ----------------------------
# Analytics Predictions
# ----------------------------

def test_get_analytics_predictions():
    """Test the predictions endpoint"""
    res = requests.get(f"{BASE_URL}/analytics/predictions")
    assert res.status_code == 200

    data = res.json()
    # Check it returns a list
    assert isinstance(data, list)

    # Check structure of first item if list is not empty
    if data:
        prediction_keys = ["cafe_name", "current_sales", "predicted_sales", "growth_percent", "rank"]
        first = data[0]
        for key in prediction_keys:
            assert key in first

        # Check types
        assert isinstance(first["cafe_name"], str)
        assert isinstance(first["current_sales"], (int, float))
        assert isinstance(first["predicted_sales"], (int, float))
        assert isinstance(first["growth_percent"], (int, float))
        assert isinstance(first["rank"], int)
