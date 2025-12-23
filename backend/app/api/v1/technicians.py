from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.database import get_db
from app.models.user import Tecnico
from app.models.lookup import LookupReparti, LookupRuoliUtente
from app.api.v1.auth import get_current_user
from pydantic import BaseModel, EmailStr
from app.core.security import get_password_hash

router = APIRouter()


class TecnicoCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    nome: str
    cognome: str
    telefono: Optional[str] = None
    cellulare: Optional[str] = None
    interno_telefonico: Optional[str] = None
    telegram_id: Optional[str] = None
    reparto_id: Optional[int] = None
    ruolo_id: int
    codice_tecnico: Optional[str] = None
    ldap_dn: Optional[str] = None
    ldap_enabled: bool = False
    username_ad: Optional[str] = None
    colore_calendario: str = "#3B82F6"
    notifiche_email: bool = True
    notifiche_push: bool = True
    note: Optional[str] = None


class TecnicoUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    nome: Optional[str] = None
    cognome: Optional[str] = None
    telefono: Optional[str] = None
    cellulare: Optional[str] = None
    interno_telefonico: Optional[str] = None
    telegram_id: Optional[str] = None
    reparto_id: Optional[int] = None
    ruolo_id: Optional[int] = None
    codice_tecnico: Optional[str] = None
    ldap_dn: Optional[str] = None
    ldap_enabled: Optional[bool] = None
    username_ad: Optional[str] = None
    colore_calendario: Optional[str] = None
    notifiche_email: Optional[bool] = None
    notifiche_push: Optional[bool] = None
    note: Optional[str] = None
    attivo: Optional[bool] = None


class RepartoResponse(BaseModel):
    id: int
    codice: str
    descrizione: str

    class Config:
        from_attributes = True


class RuoloResponse(BaseModel):
    id: int
    codice: str
    descrizione: str

    class Config:
        from_attributes = True


class TecnicoResponse(BaseModel):
    id: int
    username: str
    email: str
    nome: str
    cognome: str
    telefono: Optional[str] = None
    cellulare: Optional[str] = None
    interno_telefonico: Optional[str] = None
    telegram_id: Optional[str] = None
    reparto_id: Optional[int] = None
    reparto: Optional[RepartoResponse] = None
    ruolo_id: int
    ruolo: Optional[RuoloResponse] = None
    codice_tecnico: Optional[str] = None
    ldap_dn: Optional[str] = None
    ldap_enabled: bool
    username_ad: Optional[str] = None
    colore_calendario: str
    notifiche_email: bool
    notifiche_push: bool
    note: Optional[str] = None
    ultimo_login: Optional[datetime] = None
    attivo: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TecnicoListResponse(BaseModel):
    items: List[TecnicoResponse]
    total: int
    page: int
    limit: int


@router.get("", response_model=TecnicoListResponse)
async def get_technicians(
    page: int = 1,
    limit: int = 50,
    search: Optional[str] = None,
    reparto_id: Optional[int] = None,
    ruolo_id: Optional[int] = None,
    attivo: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: Tecnico = Depends(get_current_user)
):
    """Get list of technicians with filters"""
    query = db.query(Tecnico)

    # Filters
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (Tecnico.nome.ilike(search_filter)) |
            (Tecnico.cognome.ilike(search_filter)) |
            (Tecnico.email.ilike(search_filter)) |
            (Tecnico.username.ilike(search_filter))
        )

    if reparto_id is not None:
        query = query.filter(Tecnico.reparto_id == reparto_id)

    if ruolo_id is not None:
        query = query.filter(Tecnico.ruolo_id == ruolo_id)

    if attivo is not None:
        query = query.filter(Tecnico.attivo == attivo)

    # Count total
    total = query.count()

    # Pagination
    offset = (page - 1) * limit
    items = query.order_by(Tecnico.cognome, Tecnico.nome).offset(offset).limit(limit).all()

    return TecnicoListResponse(
        items=items,
        total=total,
        page=page,
        limit=limit
    )


@router.get("/{tecnico_id}", response_model=TecnicoResponse)
async def get_technician(
    tecnico_id: int,
    db: Session = Depends(get_db),
    current_user: Tecnico = Depends(get_current_user)
):
    """Get technician by ID"""
    tecnico = db.query(Tecnico).filter(Tecnico.id == tecnico_id).first()
    if not tecnico:
        raise HTTPException(status_code=404, detail="Technician not found")
    return tecnico


@router.post("", response_model=TecnicoResponse, status_code=status.HTTP_201_CREATED)
async def create_technician(
    data: TecnicoCreate,
    db: Session = Depends(get_db),
    current_user: Tecnico = Depends(get_current_user)
):
    """Create new technician"""
    # Check if username or email already exists
    existing = db.query(Tecnico).filter(
        (Tecnico.username == data.username) | (Tecnico.email == data.email)
    ).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Username or email already exists"
        )

    # Verify ruolo exists
    ruolo = db.query(LookupRuoliUtente).filter(LookupRuoliUtente.id == data.ruolo_id).first()
    if not ruolo:
        raise HTTPException(status_code=400, detail="Role not found")

    # Verify reparto if provided
    if data.reparto_id:
        reparto = db.query(LookupReparti).filter(LookupReparti.id == data.reparto_id).first()
        if not reparto:
            raise HTTPException(status_code=400, detail="Department not found")

    # Create technician
    tecnico = Tecnico(
        username=data.username,
        email=data.email,
        hashed_password=get_password_hash(data.password),
        nome=data.nome,
        cognome=data.cognome,
        telefono=data.telefono,
        cellulare=data.cellulare,
        interno_telefonico=data.interno_telefonico,
        telegram_id=data.telegram_id,
        reparto_id=data.reparto_id,
        ruolo_id=data.ruolo_id,
        codice_tecnico=data.codice_tecnico,
        ldap_dn=data.ldap_dn,
        ldap_enabled=int(data.ldap_enabled),
        username_ad=data.username_ad,
        colore_calendario=data.colore_calendario,
        notifiche_email=int(data.notifiche_email),
        notifiche_push=int(data.notifiche_push),
        note=data.note,
        attivo=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    db.add(tecnico)
    db.commit()
    db.refresh(tecnico)

    return tecnico


@router.put("/{tecnico_id}", response_model=TecnicoResponse)
async def update_technician(
    tecnico_id: int,
    data: TecnicoUpdate,
    db: Session = Depends(get_db),
    current_user: Tecnico = Depends(get_current_user)
):
    """Update technician"""
    tecnico = db.query(Tecnico).filter(Tecnico.id == tecnico_id).first()
    if not tecnico:
        raise HTTPException(status_code=404, detail="Technician not found")

    # Check email uniqueness if changed
    if data.email and data.email != tecnico.email:
        existing = db.query(Tecnico).filter(
            Tecnico.email == data.email,
            Tecnico.id != tecnico_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already exists")

    # Update fields
    if data.email is not None:
        tecnico.email = data.email
    if data.password is not None:
        tecnico.hashed_password = get_password_hash(data.password)
    if data.nome is not None:
        tecnico.nome = data.nome
    if data.cognome is not None:
        tecnico.cognome = data.cognome
    if data.telefono is not None:
        tecnico.telefono = data.telefono
    if data.cellulare is not None:
        tecnico.cellulare = data.cellulare
    if data.interno_telefonico is not None:
        tecnico.interno_telefonico = data.interno_telefonico
    if data.telegram_id is not None:
        tecnico.telegram_id = data.telegram_id
    if data.reparto_id is not None:
        tecnico.reparto_id = data.reparto_id
    if data.ruolo_id is not None:
        tecnico.ruolo_id = data.ruolo_id
    if data.codice_tecnico is not None:
        tecnico.codice_tecnico = data.codice_tecnico
    if data.ldap_dn is not None:
        tecnico.ldap_dn = data.ldap_dn
    if data.ldap_enabled is not None:
        tecnico.ldap_enabled = int(data.ldap_enabled)
    if data.username_ad is not None:
        tecnico.username_ad = data.username_ad
    if data.colore_calendario is not None:
        tecnico.colore_calendario = data.colore_calendario
    if data.notifiche_email is not None:
        tecnico.notifiche_email = int(data.notifiche_email)
    if data.notifiche_push is not None:
        tecnico.notifiche_push = int(data.notifiche_push)
    if data.note is not None:
        tecnico.note = data.note
    if data.attivo is not None:
        tecnico.attivo = data.attivo

    tecnico.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(tecnico)

    return tecnico


@router.delete("/{tecnico_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_technician(
    tecnico_id: int,
    db: Session = Depends(get_db),
    current_user: Tecnico = Depends(get_current_user)
):
    """Delete (deactivate) technician"""
    tecnico = db.query(Tecnico).filter(Tecnico.id == tecnico_id).first()
    if not tecnico:
        raise HTTPException(status_code=404, detail="Technician not found")

    # Don't allow deleting yourself
    if tecnico.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")

    # Soft delete (deactivate)
    tecnico.attivo = False
    tecnico.updated_at = datetime.utcnow()

    db.commit()
    return None
