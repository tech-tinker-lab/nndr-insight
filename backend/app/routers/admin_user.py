from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from app.models import User
from app.services.database_service import get_db
from app.services.auth_service import verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/admin/user", tags=["admin-user"])

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": user.username, "role": user.role})
    return {"access_token": access_token, "token_type": "bearer", "role": user.role}

@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {"username": current_user.username, "role": current_user.role, "email": current_user.email}

@router.get("/list")
def list_users(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role not in ["admin", "power_user"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    users = db.query(User).all()
    return [{"id": u.id, "username": u.username, "role": u.role, "email": u.email} for u in users]

@router.post("/create")
def create_user(new_user: dict, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role not in ["admin", "power_user"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    if db.query(User).filter(User.username == new_user["username"]).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    user = User(
        username=new_user["username"],
        password_hash=verify_password(new_user["password"]),
        role=new_user["role"],
        email=new_user.get("email", "")
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"id": user.id, "username": user.username, "role": user.role, "email": user.email} 