# Real API Service: User Management

A simple FastAPI microservice for user management, demonstrating basic CRUD operations.

## Features

*   Create, Read, Update, Delete (CRUD) users.
*   In-memory storage for demonstration purposes.
*   FastAPI for robust API development.
*   Pydantic for data validation and serialization.

## Getting Started

### Prerequisites

*   Python 3.11+
*   pip

### Local Development

1.  **Install dependencies:**
    bash
    pip install -r requirements.txt


2.  **Run the application:**
    bash
    uvicorn main:app --reload

    The API will be available at `http://127.0.0.1:8000`.
    The interactive API documentation (Swagger UI) will be at `http://127.0.0.1:8000/docs`.
    The alternative API documentation (ReDoc) will be at `http://127.0.0.1:8000/redoc`.

### Docker

1.  **Build the Docker image:**
    bash
    docker build -t real-api-service .


2.  **Run the Docker container:**
    bash
    docker run -p 8000:8000 real-api-service

    The API will be available at `http://localhost:8000`.

## API Endpoints

All endpoints are prefixed with `/`.

| Method | Endpoint          | Description               |
| :----- | :---------------- | :------------------------ |
| `GET`  | `/`               | Health check / Root       |
| `POST` | `/users/`         | Create a new user         |
| `GET`  | `/users/`         | Get all users             |
| `GET`  | `/users/{user_id}`| Get a user by ID          |
| `PUT`  | `/users/{user_id}`| Update an existing user   |
| `DELETE`|`/users/{user_id}`| Delete a user             |

## Project Structure


.
├── main.py             # Main FastAPI application
├── requirements.txt    # Python dependencies
├── Dockerfile          # Docker build instructions
└── README.md           # This file
└── pyproject.toml      # Project metadata and dependencies
└── tests/
    └── test_main.py    # Unit tests
