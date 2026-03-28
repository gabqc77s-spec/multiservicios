from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional

app = FastAPI(
    title="User Management API",
    description="A simple FastAPI microservice for user management.",
    version="0.1.0"
)

# In-memory database for demonstration purposes
users_db: Dict[int, Dict] = {}
next_user_id = 1

class UserCreate(BaseModel):
    username: str
    email: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None

class UserInDB(BaseModel):
    id: int
    username: str
    email: str

@app.get("/", summary="Root endpoint", tags=["Health"])
async def read_root():
    return {"message": "Welcome to the User Management API!"}

@app.post("/users/", response_model=UserInDB, status_code=201, summary="Create a new user", tags=["Users"])
async def create_user(user: UserCreate):
    global next_user_id
    new_user = {"id": next_user_id, "username": user.username, "email": user.email}
    users_db[next_user_id] = new_user
    next_user_id += 1
    return new_user

@app.get("/users/", response_model=List[UserInDB], summary="Get all users", tags=["Users"])
async def get_all_users():
    return list(users_db.values())

@app.get("/users/{user_id}", response_model=UserInDB, summary="Get a user by ID", tags=["Users"])
async def get_user(user_id: int):
    user = users_db.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.put("/users/{user_id}", response_model=UserInDB, summary="Update an existing user", tags=["Users"])
async def update_user(user_id: int, user_update: UserUpdate):
    user = users_db.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user_update.username is not None:
        user["username"] = user_update.username
    if user_update.email is not None:
        user["email"] = user_update.email

    users_db[user_id] = user # Update in DB
    return user

@app.delete("/users/{user_id}", status_code=204, summary="Delete a user", tags=["Users"])
async def delete_user(user_id: int):
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    del users_db[user_id]
    return