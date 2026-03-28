import pytest
from main import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_check(client):
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json == {"status": "healthy"}

def test_calculate_add(client):
    response = client.post('/calculate', json={"num1": 10, "num2": 5, "operation": "add"})
    assert response.status_code == 200
    assert response.json == {"num1": 10.0, "num2": 5.0, "operation": "add", "result": 15.0}

def test_calculate_subtract(client):
    response = client.post('/calculate', json={"num1": 10, "num2": 5, "operation": "subtract"})
    assert response.status_code == 200
    assert response.json == {"num1": 10.0, "num2": 5.0, "operation": "subtract", "result": 5.0}

def test_calculate_multiply(client):
    response = client.post('/calculate', json={"num1": 10, "num2": 5, "operation": "multiply"})
    assert response.status_code == 200
    assert response.json == {"num1": 10.0, "num2": 5.0, "operation": "multiply", "result": 50.0}

def test_calculate_divide(client):
    response = client.post('/calculate', json={"num1": 10, "num2": 5, "operation": "divide"})
    assert response.status_code == 200
    assert response.json == {"num1": 10.0, "num2": 5.0, "operation": "divide", "result": 2.0}

def test_calculate_divide_by_zero(client):
    response = client.post('/calculate', json={"num1": 10, "num2": 0, "operation": "divide"})
    assert response.status_code == 400
    assert response.json == {"error": "Cannot divide by zero"}

def test_calculate_missing_num1(client):
    response = client.post('/calculate', json={"num2": 5, "operation": "add"})
    assert response.status_code == 400
    assert response.json == {"error": "Missing num1 or num2"}

def test_calculate_invalid_json(client):
    response = client.post('/calculate', data="not json", content_type='text/plain')
    assert response.status_code == 400
    assert response.json == {"error": "Invalid JSON"}

def test_calculate_invalid_number_format(client):
    response = client.post('/calculate', json={"num1": "abc", "num2": 5, "operation": "add"})
    assert response.status_code == 400
    assert response.json == {"error": "Invalid number format"}

def test_calculate_unsupported_operation(client):
    response = client.post('/calculate', json={"num1": 10, "num2": 5, "operation": "power"})
    assert response.status_code == 400
    assert response.json == {"error": "Unsupported operation"}

def test_calculate_default_operation(client):
    response = client.post('/calculate', json={"num1": 10, "num2": 5}) # No operation specified, should default to add
    assert response.status_code == 200
    assert response.json == {"num1": 10.0, "num2": 5.0, "operation": "add", "result": 15.0}