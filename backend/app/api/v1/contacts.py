from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.database import get_db
from app.models.client import CacheReferenti, CacheClienti, SediCliente
from app.api.v1.auth import get_current_user
from app.models.user import Tecnico
from app.schemas.client import (
    ReferenteCreate,
    ReferenteUpdate,
    ReferenteResponse,
)

router = APIRouter()


@router.get("/clients/{cliente_id}/contacts", response_model=List[ReferenteResponse])
async def get_client_contacts(
    cliente_id: int,
    sede_id: Optional[int] = Query(None),
    referente_it: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: Tecnico = Depends(get_current_user)
):
    """Get all contacts for a client with optional filters"""
    # Verify client exists
    cliente = db.query(CacheClienti).filter(CacheClienti.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Client not found")

    query = db.query(CacheReferenti).filter(
        CacheReferenti.cliente_id == cliente_id,
        CacheReferenti.attivo == True
    )

    # Filters
    if sede_id is not None:
        query = query.filter(CacheReferenti.sede_id == sede_id)

    if referente_it is not None:
        query = query.filter(CacheReferenti.referente_it == int(referente_it))

    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (CacheReferenti.nome.ilike(search_filter)) |
            (CacheReferenti.cognome.ilike(search_filter)) |
            (CacheReferenti.email.ilike(search_filter))
        )

    referenti = query.order_by(
        CacheReferenti.contatto_principale.desc(),
        CacheReferenti.cognome,
        CacheReferenti.nome
    ).all()

    return referenti


@router.get("/contacts", response_model=List[ReferenteResponse])
async def get_all_contacts(
    search: Optional[str] = Query(None),
    referente_it: Optional[bool] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: Tecnico = Depends(get_current_user)
):
    """Get all contacts across all clients (rubrica generale)"""
    query = db.query(CacheReferenti).filter(CacheReferenti.attivo == True)

    # Filters
    if referente_it is not None:
        query = query.filter(CacheReferenti.referente_it == int(referente_it))

    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (CacheReferenti.nome.ilike(search_filter)) |
            (CacheReferenti.cognome.ilike(search_filter)) |
            (CacheReferenti.email.ilike(search_filter)) |
            (CacheReferenti.ruolo.ilike(search_filter))
        )

    # Pagination
    offset = (page - 1) * limit
    referenti = query.order_by(
        CacheReferenti.cognome,
        CacheReferenti.nome
    ).offset(offset).limit(limit).all()

    return referenti


@router.get("/contacts/it-referents", response_model=List[ReferenteResponse])
async def get_it_referents(
    db: Session = Depends(get_db),
    current_user: Tecnico = Depends(get_current_user)
):
    """Get all IT referents"""
    referenti = db.query(CacheReferenti).filter(
        CacheReferenti.referente_it == 1,
        CacheReferenti.attivo == True
    ).order_by(CacheReferenti.cognome, CacheReferenti.nome).all()

    return referenti


@router.get("/sites/{sede_id}/contacts", response_model=List[ReferenteResponse])
async def get_site_contacts(
    sede_id: int,
    db: Session = Depends(get_db),
    current_user: Tecnico = Depends(get_current_user)
):
    """Get all contacts for a specific site"""
    # Verify site exists
    sede = db.query(SediCliente).filter(SediCliente.id == sede_id).first()
    if not sede:
        raise HTTPException(status_code=404, detail="Site not found")

    referenti = db.query(CacheReferenti).filter(
        CacheReferenti.sede_id == sede_id,
        CacheReferenti.attivo == True
    ).order_by(CacheReferenti.cognome, CacheReferenti.nome).all()

    return referenti


@router.get("/contacts/{contatto_id}", response_model=ReferenteResponse)
async def get_contact(
    contatto_id: int,
    db: Session = Depends(get_db),
    current_user: Tecnico = Depends(get_current_user)
):
    """Get contact by ID"""
    contatto = db.query(CacheReferenti).filter(CacheReferenti.id == contatto_id).first()
    if not contatto:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contatto


@router.post("/clients/{cliente_id}/contacts", response_model=ReferenteResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(
    cliente_id: int,
    data: ReferenteCreate,
    db: Session = Depends(get_db),
    current_user: Tecnico = Depends(get_current_user)
):
    """Create new contact for a client"""
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

    # Verify sede if provided
    if data.sede_id:
        sede = db.query(SediCliente).filter(
            SediCliente.id == data.sede_id,
            SediCliente.cliente_id == cliente_id
        ).first()
        if not sede:
            raise HTTPException(
                status_code=400,
                detail="Site not found or does not belong to this client"
            )

    # Create contact
    contatto = CacheReferenti(
        codice_gestionale=data.codice_gestionale,
        cliente_id=data.cliente_id,
        sede_id=data.sede_id,
        nome=data.nome,
        cognome=data.cognome,
        ruolo=data.ruolo,
        telefono=data.telefono,
        cellulare=data.cellulare,
        interno_telefonico=data.interno_telefonico,
        email=data.email,
        contatto_principale=int(data.contatto_principale),
        riceve_notifiche=int(data.riceve_notifiche),
        referente_it=int(data.referente_it),
        note=data.note,
        ultimo_sync=datetime.utcnow(),
        attivo=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    db.add(contatto)
    db.commit()
    db.refresh(contatto)

    return contatto


@router.put("/contacts/{contatto_id}", response_model=ReferenteResponse)
async def update_contact(
    contatto_id: int,
    data: ReferenteUpdate,
    db: Session = Depends(get_db),
    current_user: Tecnico = Depends(get_current_user)
):
    """Update contact"""
    contatto = db.query(CacheReferenti).filter(CacheReferenti.id == contatto_id).first()
    if not contatto:
        raise HTTPException(status_code=404, detail="Contact not found")

    # Verify sede if changing
    if data.sede_id is not None and data.sede_id != contatto.sede_id:
        if data.sede_id:
            sede = db.query(SediCliente).filter(
                SediCliente.id == data.sede_id,
                SediCliente.cliente_id == contatto.cliente_id
            ).first()
            if not sede:
                raise HTTPException(
                    status_code=400,
                    detail="Site not found or does not belong to this client"
                )

    # Update fields
    if data.sede_id is not None:
        contatto.sede_id = data.sede_id
    if data.nome is not None:
        contatto.nome = data.nome
    if data.cognome is not None:
        contatto.cognome = data.cognome
    if data.ruolo is not None:
        contatto.ruolo = data.ruolo
    if data.telefono is not None:
        contatto.telefono = data.telefono
    if data.cellulare is not None:
        contatto.cellulare = data.cellulare
    if data.interno_telefonico is not None:
        contatto.interno_telefonico = data.interno_telefonico
    if data.email is not None:
        contatto.email = data.email
    if data.contatto_principale is not None:
        contatto.contatto_principale = int(data.contatto_principale)
    if data.riceve_notifiche is not None:
        contatto.riceve_notifiche = int(data.riceve_notifiche)
    if data.referente_it is not None:
        contatto.referente_it = int(data.referente_it)
    if data.note is not None:
        contatto.note = data.note
    if data.attivo is not None:
        contatto.attivo = data.attivo

    contatto.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(contatto)

    return contatto


@router.delete("/contacts/{contatto_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(
    contatto_id: int,
    db: Session = Depends(get_db),
    current_user: Tecnico = Depends(get_current_user)
):
    """Delete (deactivate) contact"""
    contatto = db.query(CacheReferenti).filter(CacheReferenti.id == contatto_id).first()
    if not contatto:
        raise HTTPException(status_code=404, detail="Contact not found")

    # Soft delete
    contatto.attivo = False
    contatto.updated_at = datetime.utcnow()

    db.commit()
    return None
