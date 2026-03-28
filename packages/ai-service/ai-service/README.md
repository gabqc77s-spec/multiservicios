# AI Service

A Python microservice for simple arithmetic calculations.

## Description

This service provides a `/calculate` endpoint that accepts two numbers and an operation (add, subtract, multiply, divide) to perform basic arithmetic. It's designed to be a lightweight, containerized service.

## API Endpoints

### `POST /calculate`

Performs an arithmetic operation on two numbers.

**Request Body:**

{
    "num1": 10,
    "num2": 5,
    "operation": "add"
}

`operation` can be one of: `add`, `subtract`, `multiply`, `divide`. Default is `add`.

**Response Body (Success):**

{
    "num1": 10.0,
    "num2": 5.0,
    "operation": "add",
    "result": 15.0
}


**Response Body (Error):**

{
    "error": "Missing num1 or num2"
}


### `GET /health`

Health check endpoint.

**Response Body:**

{
    "status": "healthy"
}


## How to Run Locally

1.  **Prerequisites**: Python 3.9+
2.  **Install dependencies**:
    bash
    pip install -r requirements.txt

3.  **Run the service**:
    bash
    python main.py

    The service will be available at `http://localhost:5000`.

## How to Run with Docker

1.  **Prerequisites**: Docker installed.
2.  **Build the Docker image**:
    bash
    docker build -t ai-service .

3.  **Run the Docker container**:
    bash
    docker run -p 5000:5000 ai-service

    The service will be available at `http://localhost:5000`.

## Testing

To run tests, first install `pytest` (`pip install pytest`). Then, from the `ai-service` directory:
bash
pytest tests/


**Example `POST /calculate` (add):**
bash
curl -X POST -H "Content-Type: application/json" -d '{"num1": 10, "num2": 5, "operation": "add"}' http://localhost:5000/calculate


**Example `POST /calculate` (divide):**
bash
curl -X POST -H "Content-Type: application/json" -d '{"num1": 11, "num2": 2, "operation": "divide"}' http://localhost:5000/calculate


**Example `GET /health`:**
bash
curl http://localhost:5000/health
