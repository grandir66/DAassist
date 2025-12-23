from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional
from app.database import get_db
from app.models.user import Tecnico
from app.core.security import verify_password, create_access_token, create_refresh_token, decode_token
from pydantic import BaseModel, EmailStr

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    nome: str
    cognome: str
    ruolo: str

    class Config:
        from_attributes = True


class TecnicoListItem(BaseModel):
    id: int
    nome: str
    cognome: str
    email: str
    ruolo: str

    class Config:
        from_attributes = True


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Tecnico:
    """Get current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_token(token)
    if payload is None:
        raise credentials_exception

    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception

    user = db.query(Tecnico).filter(Tecnico.username == username, Tecnico.attivo == True).first()
    if user is None:
        raise credentials_exception

    return user


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Login endpoint"""
    user = db.query(Tecnico).filter(
        Tecnico.username == form_data.username,
        Tecnico.attivo == True
    ).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Update last login
    user.ultimo_login = datetime.utcnow()
    db.commit()

    # Create tokens
    access_token = create_access_token(subject=user.username)
    refresh_token = create_refresh_token(subject=user.username)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: Tecnico = Depends(get_current_user)):
    """Get current user information"""
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        nome=current_user.nome,
        cognome=current_user.cognome,
        ruolo=current_user.ruolo.codice if current_user.ruolo else "USER"
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_token: str,
    db: Session = Depends(get_db)
):
    """Refresh access token"""
    payload = decode_token(refresh_token)
    if payload is None or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    username = payload.get("sub")
    user = db.query(Tecnico).filter(Tecnico.username == username, Tecnico.attivo == True).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    # Create new tokens
    access_token = create_access_token(subject=user.username)
    new_refresh_token = create_refresh_token(subject=user.username)

    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }


@router.get("/tecnici", response_model=list[TecnicoListItem])
async def get_tecnici(
    db: Session = Depends(get_db),
    current_user: Tecnico = Depends(get_current_user)
):
    """Get list of all active technicians"""
    tecnici = db.query(Tecnico).filter(Tecnico.attivo == True).order_by(Tecnico.cognome, Tecnico.nome).all()

    return [
        TecnicoListItem(
            id=t.id,
            nome=t.nome,
            cognome=t.cognome,
            email=t.email,
            ruolo=t.ruolo.codice if t.ruolo else "USER"
        )
        for t in tecnici
    ]
