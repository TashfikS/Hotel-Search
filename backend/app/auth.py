from flask import request, jsonify
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app.models import User
from db.db import get_db

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def authenticate_user():
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        return jsonify({"detail": "Missing credentials"}), 401

    db: Session = next(get_db())
    user = db.query(User).filter(User.username == auth.username).first()
    if not user or not verify_password(auth.password, user.password):
        return jsonify({"detail": "Incorrect username or password"}), 401

    return user

def get_current_user():
    user = authenticate_user()
    if isinstance(user, tuple):
        return user  # Return the error response if authentication failed
    return user