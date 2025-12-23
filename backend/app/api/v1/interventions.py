from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.database import get_db
from app.api.v1.auth import get_current_user
from app.models.user import Tecnico
from app.repositories.intervention import InterventionRepository
from app.schemas.intervention import (
    InterventoCreate,
    InterventoUpdate,
    InterventoResponse,
    InterventoListResponse,
    InterventoStartRequest,
    InterventoCompleteRequest,
    AttivitaInterventoCreate,
    AttivitaInterventoResponse,
    SessioneCreate,
    SessioneUpdate,
    SessioneResponse,
    RigaAttivitaUpdate,
    RigaAttivitaResponse,
)

router = APIRouter()


@router.get("", response_model=InterventoListResponse)
async def get_interventions(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    stato_id: Optional[int] = None,
    tipo_id: Optional[int] = None,
    tecnico_id: Optional[int] = None,
    cliente_id: Optional[int] = None,
    data_from: Optional[datetime] = None,
    data_to: Optional[datetime] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Tecnico = Depends(get_current_user),
):
    """Get list of interventions with pagination and filters"""
    repo = InterventionRepository(db)

    skip = (page - 1) * limit
    interventi, total = repo.get_all(
        skip=skip,
        limit=limit,
        stato_id=stato_id,
        tipo_id=tipo_id,
        tecnico_id=tecnico_id,
        cliente_id=cliente_id,
        data_from=data_from,
        data_to=data_to,
        search=search,
    )

    return InterventoListResponse(
        total=total,
        page=page,
        limit=limit,
        interventi=[InterventoResponse.model_validate(i) for i in interventi],
    )


@router.post("", response_model=InterventoResponse, status_code=201)
async def create_intervention(
    intervento_data: InterventoCreate,
    db: Session = Depends(get_db),
    current_user: Tecnico = Depends(get_current_user),
):
    """Create new intervention"""
    repo = InterventionRepository(db)

    intervento = repo.create(intervento_data)

    return InterventoResponse.model_validate(intervento)


@router.get("/{intervento_id}", response_model=InterventoResponse)
async def get_intervention(
    intervento_id: int,
    db: Session = Depends(get_db),
    current_user: Tecnico = Depends(get_current_user),
):
    """Get intervention details"""
    repo = InterventionRepository(db)

    intervento = repo.get_by_id(intervento_id)
    if not intervento:
        raise HTTPException(status_code=404, detail="Intervento non trovato")

    return InterventoResponse.model_validate(intervento)


@router.patch("/{intervento_id}", response_model=InterventoResponse)
async def update_intervention(
    intervento_id: int,
    update_data: InterventoUpdate,
    db: Session = Depends(get_db),
    current_user: Tecnico = Depends(get_current_user),
):
    """Update intervention"""
    repo = InterventionRepository(db)

    intervento = repo.get_by_id(intervento_id)
    if not intervento:
        raise HTTPException(status_code=404, detail="Intervento non trovato")

    # Check if intervention is already completed
    if intervento.stato and intervento.stato.finale:
        raise HTTPException(
            status_code=400, detail="Non è possibile modificare un intervento completato"
        )

    intervento = repo.update(intervento, update_data)

    return InterventoResponse.model_validate(intervento)


@router.post("/{intervento_id}/start", response_model=InterventoResponse)
async def start_intervention(
    intervento_id: int,
    request_data: InterventoStartRequest,
    db: Session = Depends(get_db),
    current_user: Tecnico = Depends(get_current_user),
):
    """Start intervention"""
    repo = InterventionRepository(db)

    intervento = repo.get_by_id(intervento_id)
    if not intervento:
        raise HTTPException(status_code=404, detail="Intervento non trovato")

    # Check if already started
    if intervento.data_inizio:
        raise HTTPException(status_code=400, detail="Intervento già avviato")

    # Check if intervention is assigned to current user
    if intervento.tecnico_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Non sei assegnato a questo intervento"
        )

    intervento = repo.start(intervento, request_data.note_avvio)

    return InterventoResponse.model_validate(intervento)


@router.post("/{intervento_id}/complete", response_model=InterventoResponse)
async def complete_intervention(
    intervento_id: int,
    request_data: InterventoCompleteRequest,
    db: Session = Depends(get_db),
    current_user: Tecnico = Depends(get_current_user),
):
    """Complete intervention"""
    repo = InterventionRepository(db)

    intervento = repo.get_by_id(intervento_id)
    if not intervento:
        raise HTTPException(status_code=404, detail="Intervento non trovato")

    # Check if already completed
    if intervento.data_fine:
        raise HTTPException(status_code=400, detail="Intervento già completato")

    # Check if intervention is assigned to current user
    if intervento.tecnico_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Non sei assegnato a questo intervento"
        )

    intervento = repo.complete(
        intervento,
        descrizione_lavoro=request_data.descrizione_lavoro,
        firma_cliente=request_data.firma_cliente,
        firma_nome=request_data.firma_nome,
        firma_ruolo=request_data.firma_ruolo,
    )

    return InterventoResponse.model_validate(intervento)


@router.post("/{intervento_id}/attivita", response_model=AttivitaInterventoResponse, status_code=201)
async def add_intervention_activity(
    intervento_id: int,
    attivita_data: AttivitaInterventoCreate,
    db: Session = Depends(get_db),
    current_user: Tecnico = Depends(get_current_user),
):
    """Add activity to intervention"""
    repo = InterventionRepository(db)

    # Verify intervention exists
    intervento = repo.get_by_id(intervento_id)
    if not intervento:
        raise HTTPException(status_code=404, detail="Intervento non trovato")

    # Check if intervention is completed
    if intervento.stato and intervento.stato.finale:
        raise HTTPException(
            status_code=400, detail="Non è possibile aggiungere attività a un intervento completato"
        )

    attivita = repo.add_attivita(intervento_id, attivita_data)

    # Return with categoria descrizione
    from app.models.lookup import LookupCategorieAttivita

    categoria = db.query(LookupCategorieAttivita).filter_by(id=attivita.categoria_id).first()

    response_data = attivita.__dict__.copy()
    response_data["categoria_descrizione"] = categoria.descrizione if categoria else ""

    return AttivitaInterventoResponse.model_validate(response_data)


@router.delete("/{intervento_id}", status_code=204)
async def delete_intervention(
    intervento_id: int,
    db: Session = Depends(get_db),
    current_user: Tecnico = Depends(get_current_user),
):
    """Delete (soft) intervention"""
    repo = InterventionRepository(db)

    intervento = repo.get_by_id(intervento_id)
    if not intervento:
        raise HTTPException(status_code=404, detail="Intervento non trovato")

    # Check if intervention is completed
    if intervento.stato and intervento.stato.finale:
        raise HTTPException(
            status_code=400, detail="Non è possibile eliminare un intervento completato"
        )

    repo.delete(intervento)

    return None


# ============================================================================
# SESSIONI LAVORO (Tempi)
# ============================================================================

@router.get("/{intervento_id}/sessions", response_model=list[SessioneResponse])
async def get_intervention_sessions(
    intervento_id: int,
    db: Session = Depends(get_db),
    current_user: Tecnico = Depends(get_current_user),
):
    """Get all work sessions for an intervention"""
    repo = InterventionRepository(db)

    # Verify intervention exists
    intervento = repo.get_by_id(intervento_id)
    if not intervento:
        raise HTTPException(status_code=404, detail="Intervento non trovato")

    sessioni = repo.get_sessioni(intervento_id)

    return [SessioneResponse.model_validate(s) for s in sessioni]


@router.post("/{intervento_id}/sessions", response_model=SessioneResponse, status_code=201)
async def add_intervention_session(
    intervento_id: int,
    sessione_data: SessioneCreate,
    db: Session = Depends(get_db),
    current_user: Tecnico = Depends(get_current_user),
):
    """Add work session to intervention"""
    repo = InterventionRepository(db)

    # Verify intervention exists
    intervento = repo.get_by_id(intervento_id)
    if not intervento:
        raise HTTPException(status_code=404, detail="Intervento non trovato")

    # Check if intervention is completed
    if intervento.stato and intervento.stato.finale:
        raise HTTPException(
            status_code=400,
            detail="Non è possibile aggiungere sessioni a un intervento completato",
        )

    sessione = repo.add_sessione(intervento_id, current_user.id, sessione_data)

    return SessioneResponse.model_validate(sessione)


@router.patch("/{intervento_id}/sessions/{session_id}", response_model=SessioneResponse)
async def update_intervention_session(
    intervento_id: int,
    session_id: int,
    update_data: SessioneUpdate,
    db: Session = Depends(get_db),
    current_user: Tecnico = Depends(get_current_user),
):
    """Update work session"""
    repo = InterventionRepository(db)

    # Verify intervention exists
    intervento = repo.get_by_id(intervento_id)
    if not intervento:
        raise HTTPException(status_code=404, detail="Intervento non trovato")

    try:
        sessione = repo.update_sessione(session_id, update_data)
        return SessioneResponse.model_validate(sessione)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{intervento_id}/sessions/{session_id}", status_code=204)
async def delete_intervention_session(
    intervento_id: int,
    session_id: int,
    db: Session = Depends(get_db),
    current_user: Tecnico = Depends(get_current_user),
):
    """Delete work session"""
    repo = InterventionRepository(db)

    # Verify intervention exists
    intervento = repo.get_by_id(intervento_id)
    if not intervento:
        raise HTTPException(status_code=404, detail="Intervento non trovato")

    try:
        repo.delete_sessione(session_id)
        return None
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ============================================================================
# RIGHE ATTIVITÀ (CRUD Completo)
# ============================================================================

@router.get("/{intervento_id}/rows", response_model=list[RigaAttivitaResponse])
async def get_intervention_rows(
    intervento_id: int,
    db: Session = Depends(get_db),
    current_user: Tecnico = Depends(get_current_user),
):
    """Get all activity rows for an intervention"""
    repo = InterventionRepository(db)

    # Verify intervention exists
    intervento = repo.get_by_id(intervento_id)
    if not intervento:
        raise HTTPException(status_code=404, detail="Intervento non trovato")

    righe = repo.get_righe(intervento_id)

    return [RigaAttivitaResponse.model_validate(r) for r in righe]


@router.patch("/{intervento_id}/rows/{row_id}", response_model=RigaAttivitaResponse)
async def update_intervention_row(
    intervento_id: int,
    row_id: int,
    update_data: RigaAttivitaUpdate,
    db: Session = Depends(get_db),
    current_user: Tecnico = Depends(get_current_user),
):
    """Update activity row"""
    repo = InterventionRepository(db)

    # Verify intervention exists
    intervento = repo.get_by_id(intervento_id)
    if not intervento:
        raise HTTPException(status_code=404, detail="Intervento non trovato")

    try:
        riga = repo.update_riga(row_id, update_data)
        return RigaAttivitaResponse.model_validate(riga)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{intervento_id}/rows/{row_id}", status_code=204)
async def delete_intervention_row(
    intervento_id: int,
    row_id: int,
    db: Session = Depends(get_db),
    current_user: Tecnico = Depends(get_current_user),
):
    """Delete activity row"""
    repo = InterventionRepository(db)

    # Verify intervention exists
    intervento = repo.get_by_id(intervento_id)
    if not intervento:
        raise HTTPException(status_code=404, detail="Intervento non trovato")

    try:
        repo.delete_riga(row_id)
        return None
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
