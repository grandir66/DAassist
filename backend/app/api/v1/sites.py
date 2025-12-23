from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.database import get_db
from app.models.client import SediCliente, CacheClienti
from app.api.v1.auth import get_current_user
from app.models.user import Tecnico
from app.schemas.client import (
    SedeClienteCreate,
    SedeClienteUpdate,
    SedeClienteResponse,
)

router = APIRouter()


@router.get("/clients/{cliente_id}/sites", response_model=List[SedeClienteResponse])
async def get_client_sites(
    cliente_id: int,
    db: Session = Depends(get_db),
    current_user: Tecnico = Depends(get_current_user)
):
    """Get all sites for a client"""
    # Verify client exists
    cliente = db.query(CacheClienti).filter(CacheClienti.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Client not found")

    sedi = db.query(SediCliente).filter(
        SediCliente.cliente_id == cliente_id,
        SediCliente.attivo == True
    ).order_by(SediCliente.nome_sede).all()

    return sedi


@router.get("/sites/{sede_id}", response_model=SedeClienteResponse)
async def get_site(
    sede_id: int,
    db: Session = Depends(get_db),
    current_user: Tecnico = Depends(get_current_user)
):
    """Get site by ID"""
    sede = db.query(SediCliente).filter(SediCliente.id == sede_id).first()
    if not sede:
        raise HTTPException(status_code=404, detail="Site not found")
    return sede


@router.post("/clients/{cliente_id}/sites", response_model=SedeClienteResponse, status_code=status.HTTP_201_CREATED)
async def create_site(
    cliente_id: int,
    data: SedeClienteCreate,
    db: Session = Depends(get_db),
    current_user: Tecnico = Depends(get_current_user)
):
    """Create new site for a client"""
    # Verify client exists
    cliente = db.query(CacheClienti).filter(CacheClienti.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Client not found")

    # Ensure cliente_id matches
    if data.cliente_id != cliente_id:
        raise HTTPException(
            status_code=400,
            detail="cliente_id in body must match cliente_id in URL"
        )

    # Create site
    sede = SediCliente(
        cliente_id=data.cliente_id,
        nome_sede=data.nome_sede,
        codice_sede=data.codice_sede,
        indirizzo=data.indirizzo,
        cap=data.cap,
        citta=data.citta,
        provincia=data.provincia,
        nazione=data.nazione,
        telefono=data.telefono,
        email=data.email,
        orari_servizio=data.orari_servizio,
        note=data.note,
        attivo=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    db.add(sede)
    db.commit()
    db.refresh(sede)

    return sede


@router.put("/sites/{sede_id}", response_model=SedeClienteResponse)
async def update_site(
    sede_id: int,
    data: SedeClienteUpdate,
    db: Session = Depends(get_db),
    current_user: Tecnico = Depends(get_current_user)
):
    """Update site"""
    sede = db.query(SediCliente).filter(SediCliente.id == sede_id).first()
    if not sede:
        raise HTTPException(status_code=404, detail="Site not found")

    # Update fields
    if data.nome_sede is not None:
        sede.nome_sede = data.nome_sede
    if data.codice_sede is not None:
        sede.codice_sede = data.codice_sede
    if data.indirizzo is not None:
        sede.indirizzo = data.indirizzo
    if data.cap is not None:
        sede.cap = data.cap
    if data.citta is not None:
        sede.citta = data.citta
    if data.provincia is not None:
        sede.provincia = data.provincia
    if data.nazione is not None:
        sede.nazione = data.nazione
    if data.telefono is not None:
        sede.telefono = data.telefono
    if data.email is not None:
        sede.email = data.email
    if data.orari_servizio is not None:
        sede.orari_servizio = data.orari_servizio
    if data.note is not None:
        sede.note = data.note
    if data.attivo is not None:
        sede.attivo = data.attivo

    sede.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(sede)

    return sede


@router.delete("/sites/{sede_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_site(
    sede_id: int,
    db: Session = Depends(get_db),
    current_user: Tecnico = Depends(get_current_user)
):
    """Delete (deactivate) site"""
    sede = db.query(SediCliente).filter(SediCliente.id == sede_id).first()
    if not sede:
        raise HTTPException(status_code=404, detail="Site not found")

    # Soft delete
    sede.attivo = False
    sede.updated_at = datetime.utcnow()

    db.commit()
    return None
