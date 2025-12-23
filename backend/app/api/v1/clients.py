from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.api.v1.auth import get_current_user
from app.models.user import Tecnico
from app.repositories.client import ClientRepository
from app.schemas.client import (
    ClienteResponse,
    ClienteListResponse,
    ClienteDetailResponse,
    ContrattoResponse,
    ReferenteResponse,
)

router = APIRouter()


@router.get("", response_model=ClienteListResponse)
async def get_clients(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    attivo: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    current_user: Tecnico = Depends(get_current_user),
):
    """Get list of clients with pagination and filters"""
    repo = ClientRepository(db)

    skip = (page - 1) * limit
    clienti, total = repo.get_all(
        skip=skip,
        limit=limit,
        search=search,
        attivo=attivo,
    )

    return ClienteListResponse(
        total=total,
        page=page,
        limit=limit,
        clienti=[ClienteResponse.model_validate(c) for c in clienti],
    )


@router.get("/{cliente_id}", response_model=ClienteDetailResponse)
async def get_client(
    cliente_id: int,
    db: Session = Depends(get_db),
    current_user: Tecnico = Depends(get_current_user),
):
    """Get client details with contracts and contacts"""
    repo = ClientRepository(db)

    cliente = repo.get_by_id(cliente_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente non trovato")

    # Load related data
    contratti = repo.get_contratti(cliente_id)
    referenti = repo.get_referenti(cliente_id)

    # Load sedi from sites endpoint
    from app.models.client import SediCliente
    sedi = db.query(SediCliente).filter(
        SediCliente.cliente_id == cliente_id,
        SediCliente.attivo == True
    ).all()

    # Build response with related data
    cliente_dict = ClienteResponse.model_validate(cliente).model_dump()
    cliente_dict['contratti'] = [ContrattoResponse.model_validate(c) for c in contratti]
    cliente_dict['referenti'] = [ReferenteResponse.model_validate(r) for r in referenti]
    cliente_dict['sedi'] = [c for c in sedi]  # Will be validated by response_model

    return cliente_dict


@router.get("/{cliente_id}/contratti", response_model=list[ContrattoResponse])
async def get_client_contracts(
    cliente_id: int,
    db: Session = Depends(get_db),
    current_user: Tecnico = Depends(get_current_user),
):
    """Get all contracts for a client"""
    repo = ClientRepository(db)

    # Verify client exists
    cliente = repo.get_by_id(cliente_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente non trovato")

    contratti = repo.get_contratti(cliente_id)
    return [ContrattoResponse.model_validate(c) for c in contratti]


@router.get("/{cliente_id}/referenti", response_model=list[ReferenteResponse])
async def get_client_contacts(
    cliente_id: int,
    db: Session = Depends(get_db),
    current_user: Tecnico = Depends(get_current_user),
):
    """Get all contacts for a client"""
    repo = ClientRepository(db)

    # Verify client exists
    cliente = repo.get_by_id(cliente_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente non trovato")

    referenti = repo.get_referenti(cliente_id)
    return [ReferenteResponse.model_validate(r) for r in referenti]


@router.get("/{cliente_id}/stats")
async def get_client_stats(
    cliente_id: int,
    db: Session = Depends(get_db),
    current_user: Tecnico = Depends(get_current_user),
):
    """Get statistics for a client"""
    repo = ClientRepository(db)

    # Verify client exists
    cliente = repo.get_by_id(cliente_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente non trovato")

    stats = repo.get_stats(cliente_id)
    return stats
