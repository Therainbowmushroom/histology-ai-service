from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.models.user import User

from app.auth.passwords import hash_password
from app.auth.auth import authenticate_user
from app.auth.jwt import create_access_token

from app.schemas.auth import RegisterRequest
from app.schemas.auth import LoginRequest


router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

#class UserCreds(BaseModel):
  #  username: str
  #  password: str

class AuthRequest(BaseModel):
    username: str
    password: str

# ======================================
# REGISTER
# ======================================

@router.post("/register")
def register(data: AuthRequest, db: Session = Depends(get_db)):
    hashed = hash_password(data.password)
    user = User(username=data.username, password_hash=hashed)
    db.add(user)
    db.commit()
    return {"message": "registered"}

# ======================================
# LOGIN
# ======================================

@router.post("/login")
def login(data: AuthRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, data.username, data.password)
    if not user:
        return {"error": "invalid credentials"}
    token = create_access_token({"sub": user.username})
    return {"access_token": token}