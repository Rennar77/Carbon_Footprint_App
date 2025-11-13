from fastapi import APIRouter, HTTPException
from schemas.user_schema import UserLogin, UserRegister
from services.auth_service import create_user, verify_password, create_access_token
from core.database import get_db

import psycopg2

router = APIRouter(tags=["Auth"])

@router.post("/register")
def register(user: UserRegister):
    success = create_user(user.name, user.email, user.password)
    if not success:
        raise HTTPException(status_code=400, detail="User already exists")

    token = create_access_token({"sub": user.email})
    return {"success": True, "message": "User created", "token": token}

@router.post("/login")
def login(user: UserLogin):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, password FROM users WHERE email=%s", (user.email,))
    record = cur.fetchone()
    cur.close()
    conn.close()

    if not record:
        raise HTTPException(status_code=404, detail="User not found")

    user_id, hashed_pw = record
    if not verify_password(user.password, hashed_pw):
        raise HTTPException(status_code=401, detail="Incorrect password")

    token = create_access_token({"sub": str(user_id)})
    return {"success": True, "token": token}
