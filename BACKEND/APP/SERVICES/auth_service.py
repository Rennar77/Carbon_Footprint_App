from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
import os

# -----------------------------
# Load env
# -----------------------------
load_dotenv()  # loads variables from .env

SECRET_KEY = os.getenv("JWT_SECRET")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

DB_PARAMS = {
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}

# -----------------------------
# Router setup
# -----------------------------
router = APIRouter(tags=["auth"])



def get_db():
    conn = psycopg2.connect(**DB_PARAMS)
    conn.autocommit = True
    return conn


# -----------------------------
# User creation (signup)
# -----------------------------
def create_user(name: str, email: str, password: str) -> bool:
    """Create a new user. Returns True if successful, False if user already exists."""
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Check if email already exists
    cur.execute("SELECT id FROM users WHERE email=%s", (email,))
    if cur.fetchone():
        cur.close()
        conn.close()
        return False  # user exists

    # Hash password
    hashed_password = hash_password(password)

    # Insert user
    cur.execute(
        "INSERT INTO users (name, email, password) VALUES (%s, %s, %s) RETURNING id",
        (name, email, hashed_password)
    )
    cur.close()
    conn.close()
    return True


# -----------------------------
# Password helpers
# -----------------------------
def hash_password(password: str) -> str:
    truncated = password[:72]  # bcrypt limit
    return pwd_context.hash(truncated)

def verify_password(password: str, hashed: str) -> bool:
    truncated = password[:72]
    return pwd_context.verify(truncated, hashed)


# -----------------------------
# JWT helpers
# -----------------------------
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")

        conn = get_db()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("SELECT id, name, email FROM users WHERE id=%s", (user_id,))
        user = cur.fetchone()
        cur.close()
        conn.close()

        if not user:
            raise HTTPException(status_code=401, detail="User not found")

        return {"id": user["id"], "name": user["name"], "email": user["email"]}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


# -----------------------------
# Auth routes
# -----------------------------
@router.post("/signup")
def signup(name: str, email: str, password: str):
    success = create_user(name, email, password)
    if not success:
        raise HTTPException(status_code=400, detail="User already exists")
    return {"message": "User created successfully"}


@router.post("/login")
async def login(request: Request):
    data = await request.json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password required")

    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT * FROM users WHERE email=%s", (email,))
    user = cur.fetchone()

    if not user or not verify_password(password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": str(user["id"])})
    cur.close()
    conn.close()

    return {"token": token, "user": {"id": user["id"], "name": user["name"], "email": user["email"]}}
