"""Router de autenticacion."""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ..auth import authenticate, create_access_token, get_current_user
from ..database import get_db
from ..models import User
from ..schemas import Token, UserOut

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=Token)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate(db, form.username, form.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Usuario o contrasena incorrectos")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Cuenta desactivada")
    return Token(access_token=create_access_token(user.username))


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return user
