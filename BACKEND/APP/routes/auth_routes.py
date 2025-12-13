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
import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta

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
# --------------------------
# Email Configuration
# --------------------------
SMTP_SERVER = os.getenv("EMAIL_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASS")
RESET_URL = os.getenv("RESET_PASSWORD_URL", "http://localhost:3000/reset-password")

def send_reset_email(to_email: str, reset_token: str, user_id: int):
    """Send password reset email"""
    if not EMAIL_USER or not EMAIL_PASSWORD:
        print("Email credentials not configured. Skipping email send.")
        return False
    
    try:
        # For mobile apps, you might want to use a deeplink
        reset_link = f"{RESET_URL}?token={reset_token}&user_id={user_id}"
        
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = to_email
        msg['Subject'] = "Password Reset - EcoTrack"
        
        body = f"""
        <html>
        <body>
            <h2>Password Reset Request</h2>
            <p>You requested to reset your password for your EcoTrack account.</p>
            <p>Click the link below to reset your password:</p>
            <p><a href="{reset_link}" style="background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Reset Password</a></p>
            <p>Or copy this token to use in the app: <strong>{reset_token}</strong></p>
            <p>This link will expire in 1 hour.</p>
            <p>If you didn't request this, please ignore this email.</p>
            <br>
            <p>Best regards,<br>EcoTrack Team</p>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(body, 'html'))
        
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            server.send_message(msg)
        
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

# --------------------------
# Forgot Password Routes
# --------------------------
@router.post("/forgot-password")
def forgot_password(email: str):
    """Generate and send password reset token"""
    conn = get_db()
    cur = conn.cursor()
    
    # Check if user exists
    cur.execute("SELECT id, email FROM users WHERE email=%s", (email,))
    user = cur.fetchone()
    
    if not user:
        cur.close()
        conn.close()
        # Return success even if user doesn't exist (security best practice)
        return {"success": True, "message": "If your email exists, you will receive reset instructions"}
    
    user_id = user[0]
    
    # Generate reset token
    reset_token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(hours=1)
    
    # Store token in database (create password_resets table)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS password_resets (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            token TEXT NOT NULL UNIQUE,
            expires_at TIMESTAMP NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Delete any existing tokens for this user
    cur.execute("DELETE FROM password_resets WHERE user_id=%s", (user_id,))
    
    # Insert new token
    cur.execute(
        "INSERT INTO password_resets (user_id, token, expires_at) VALUES (%s, %s, %s)",
        (user_id, reset_token, expires_at)
    )
    
    conn.commit()
    cur.close()
    conn.close()
    
    # Send email
    email_sent = send_reset_email(email, reset_token, user_id)
    
    if not email_sent and EMAIL_USER:  # Only warn if email was configured
        return {
            "success": False, 
            "message": "Could not send email. Please try again later."
        }
    
    return {
        "success": True, 
        "message": "If your email exists, you will receive reset instructions",
        "token": reset_token  # For testing/demo - remove in production
    }

@router.post("/reset-password")
def reset_password(token: str, new_password: str, user_id: int = None):
    """Reset password using token"""
    conn = get_db()
    cur = conn.cursor()
    
    # Clean up expired tokens first
    cur.execute("DELETE FROM password_resets WHERE expires_at < NOW()")
    
    # Find valid token
    if user_id:
        cur.execute(
            "SELECT * FROM password_resets WHERE token=%s AND user_id=%s",
            (token, user_id)
        )
    else:
        cur.execute("SELECT * FROM password_resets WHERE token=%s", (token,))
    
    reset_record = cur.fetchone()
    
    if not reset_record:
        cur.close()
        conn.close()
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
    
    # Hash new password
    hashed_password = hash_password(new_password)
    
    # Update user password
    cur.execute(
        "UPDATE users SET password=%s WHERE id=%s",
        (hashed_password, reset_record[1])  # reset_record[1] is user_id
    )
    
    # Delete used token
    cur.execute("DELETE FROM password_resets WHERE token=%s", (token,))
    
    conn.commit()
    cur.close()
    conn.close()
    
    return {"success": True, "message": "Password reset successful"}

@router.post("/verify-reset-token")
def verify_reset_token(token: str, user_id: int = None):
    """Verify if a reset token is valid"""
    conn = get_db()
    cur = conn.cursor()
    
    # Clean up expired tokens
    cur.execute("DELETE FROM password_resets WHERE expires_at < NOW()")
    
    # Check token
    if user_id:
        cur.execute(
            "SELECT * FROM password_resets WHERE token=%s AND user_id=%s",
            (token, user_id)
        )
    else:
        cur.execute("SELECT * FROM password_resets WHERE token=%s", (token,))
    
    reset_record = cur.fetchone()
    
    cur.close()
    conn.close()
    
    if not reset_record:
        return {"valid": False, "message": "Invalid or expired token"}
    
    return {"valid": True, "user_id": reset_record[1]}