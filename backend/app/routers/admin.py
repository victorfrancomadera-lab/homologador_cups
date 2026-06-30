"""Router de administracion de usuarios (solo admin)."""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..auth import hash_password, require_admin
from ..database import get_db
from ..models import User
from ..schemas import UserCreate, UserOut, UserUpdate

router = APIRouter(prefix="/api/admin/users", tags=["admin"],
                   dependencies=[Depends(require_admin)])


@router.get("", response_model=List[UserOut])
def list_users(db: Session = Depends(get_db)):
    return db.query(User).order_by(User.id).all()


@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(data: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == data.username).first():
        raise HTTPException(status_code=400, detail="El nombre de usuario ya existe")
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=400, detail="El correo ya esta registrado")
    user = User(
        username=data.username, email=data.email, full_name=data.full_name,
        hashed_password=hash_password(data.password), is_active=data.is_active,
        is_admin=data.is_admin, can_view_soat=data.can_view_soat,
        can_view_iss=data.can_view_iss,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.put("/{user_id}", response_model=UserOut)
def update_user(user_id: int, data: UserUpdate, db: Session = Depends(get_db),
                admin: User = Depends(require_admin)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    payload = data.model_dump(exclude_unset=True)
    if "password" in payload and payload["password"]:
        user.hashed_password = hash_password(payload.pop("password"))
    else:
        payload.pop("password", None)
    # Evita que el admin se quite a si mismo el rol o se desactive
    if user.id == admin.id:
        payload.pop("is_admin", None)
        payload.pop("is_active", None)
    if "email" in payload:
        clash = db.query(User).filter(User.email == payload["email"],
                                       User.id != user_id).first()
        if clash:
            raise HTTPException(status_code=400, detail="El correo ya esta registrado")
    for k, v in payload.items():
        setattr(user, k, v)
    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db),
                admin: User = Depends(require_admin)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    if user.id == admin.id:
        raise HTTPException(status_code=400, detail="No puede eliminar su propia cuenta")
    db.delete(user)
    db.commit()
