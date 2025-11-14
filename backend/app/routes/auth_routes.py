# lib/services/auth_routes.py (or wherever your auth router is)
from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from typing import Optional
from app.services.auth_service import create_user, verify_password, create_access_token, hash_password
from app.core.database import get_db
from app.schemas.user_schema import UserLogin, UserRegister, UserUpdate
import psycopg2
import psycopg2.extras
import shutil
import os
from dotenv import load_dotenv

# --------------------------
# Load environment variables
# --------------------------
load_dotenv()
SECRET_KEY = os.getenv("JWT_SECRET")
ALGORITHM = "HS256"

router = APIRouter(tags=["Auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

UPLOAD_DIR = "static/profile_pics"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# --------------------------
# JWT Helper
# --------------------------
def get_current_user(token: str = Depends(oauth2_scheme)) -> int:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# --------------------------
# Auth Routes
# --------------------------
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

# --------------------------
# Profile Routes
# --------------------------
@router.get("/profile")
def get_profile(current_user: int = Depends(get_current_user)):
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    cur.execute(
        "SELECT id, name, email, username, profile_picture FROM users WHERE id=%s",
        (current_user,)
    )
    row = cur.fetchone()
    cur.close()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="User not found")

    if row["profile_picture"]:
        row["profile_picture"] = f"/{row['profile_picture']}"

    return row

@router.put("/profile")
def update_profile(data: UserUpdate, current_user: int = Depends(get_current_user)):
    conn = get_db()
    cur = conn.cursor()

    if data.username:
        cur.execute("UPDATE users SET username=%s WHERE id=%s", (data.username, current_user))
    if data.email:
        cur.execute("UPDATE users SET email=%s WHERE id=%s", (data.email, current_user))
    if data.password:
        hashed_pw = hash_password(data.password)
        cur.execute("UPDATE users SET password=%s WHERE id=%s", (hashed_pw, current_user))

    conn.commit()
    cur.close()
    conn.close()
    return {"success": True, "message": "Profile updated"}

@router.post("/profile/upload-picture")
def upload_profile_picture(file: UploadFile = File(...), current_user: int = Depends(get_current_user)):
    file_ext = os.path.splitext(file.filename)[1]
    file_path = os.path.join(UPLOAD_DIR, f"user_{current_user}{file_ext}")

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    conn = get_db()
    cur = conn.cursor()
    cur.execute("UPDATE users SET profile_picture=%s WHERE id=%s", (file_path, current_user))
    conn.commit()
    cur.close()
    conn.close()

    return {"success": True, "profile_picture": f"/{file_path}"}

@router.delete("/profile")
def delete_account(current_user: int = Depends(get_current_user)):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE id=%s", (current_user,))
    conn.commit()
    cur.close()
    conn.close()
    return {"success": True, "message": "Account deleted successfully"}
