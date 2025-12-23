from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.lookup import (
    LookupCanaliRichiesta,
    LookupPriorita,
    LookupStatiTicket,
    LookupStatiIntervento,
    LookupTipiIntervento,
    LookupCategorieAttivita,
    LookupOriginiIntervento,
    LookupReparti,
    LookupRuoliUtente,
    LookupStatiCliente,
    LookupClassificazioniCliente,
)
from pydantic import BaseModel

router = APIRouter()


# Pydantic schemas
class LookupBase(BaseModel):
    id: int
    codice: str
    descrizione: str
    attivo: bool

    class Config:
        from_attributes = True


class PrioritaSchema(LookupBase):
    livello: int
    colore: str


class StatoSchema(LookupBase):
    colore: str
    finale: bool


class ClassificazioneSchema(LookupBase):
    colore: str


class TipoInterventoSchema(LookupBase):
    colore: str
    richiede_viaggio: bool


class CategoriaAttivitaSchema(LookupBase):
    prezzo_unitario_default: float


class RepartoSchema(LookupBase):
    email: Optional[str] = None


# Endpoints
@router.get("/channels", response_model=List[LookupBase])
async def get_canali_richiesta(
    attivo: bool = Query(True),
    db: Session = Depends(get_db)
):
    """Get all request channels"""
    query = db.query(LookupCanaliRichiesta)
    if attivo is not None:
        query = query.filter(LookupCanaliRichiesta.attivo == attivo)
    return query.order_by(LookupCanaliRichiesta.ordine).all()


@router.get("/priorities", response_model=List[PrioritaSchema])
async def get_priorita(
    attivo: bool = Query(True),
    db: Session = Depends(get_db)
):
    """Get all priorities"""
    query = db.query(LookupPriorita)
    if attivo is not None:
        query = query.filter(LookupPriorita.attivo == attivo)
    return query.order_by(LookupPriorita.livello).all()


@router.get("/ticket-states", response_model=List[StatoSchema])
async def get_stati_ticket(
    attivo: bool = Query(True),
    db: Session = Depends(get_db)
):
    """Get all ticket states"""
    query = db.query(LookupStatiTicket)
    if attivo is not None:
        query = query.filter(LookupStatiTicket.attivo == attivo)
    return query.order_by(LookupStatiTicket.ordine).all()


@router.get("/intervention-states", response_model=List[StatoSchema])
async def get_stati_intervento(
    attivo: bool = Query(True),
    db: Session = Depends(get_db)
):
    """Get all intervention states"""
    query = db.query(LookupStatiIntervento)
    if attivo is not None:
        query = query.filter(LookupStatiIntervento.attivo == attivo)
    return query.order_by(LookupStatiIntervento.ordine).all()


@router.get("/intervention-types", response_model=List[TipoInterventoSchema])
async def get_tipi_intervento(
    attivo: bool = Query(True),
    db: Session = Depends(get_db)
):
    """Get all intervention types"""
    query = db.query(LookupTipiIntervento)
    if attivo is not None:
        query = query.filter(LookupTipiIntervento.attivo == attivo)
    return query.order_by(LookupTipiIntervento.ordine).all()


@router.get("/activity-categories", response_model=List[CategoriaAttivitaSchema])
async def get_categorie_attivita(
    attivo: bool = Query(True),
    db: Session = Depends(get_db)
):
    """Get all activity categories"""
    query = db.query(LookupCategorieAttivita)
    if attivo is not None:
        query = query.filter(LookupCategorieAttivita.attivo == attivo)
    return query.order_by(LookupCategorieAttivita.ordine).all()


@router.get("/intervention-origins", response_model=List[LookupBase])
async def get_origini_intervento(
    attivo: bool = Query(True),
    db: Session = Depends(get_db)
):
    """Get all intervention origins"""
    query = db.query(LookupOriginiIntervento)
    if attivo is not None:
        query = query.filter(LookupOriginiIntervento.attivo == attivo)
    return query.order_by(LookupOriginiIntervento.ordine).all()


@router.get("/departments", response_model=List[RepartoSchema])
async def get_reparti(
    attivo: bool = Query(True),
    db: Session = Depends(get_db)
):
    """Get all departments"""
    query = db.query(LookupReparti)
    if attivo is not None:
        query = query.filter(LookupReparti.attivo == attivo)
    return query.order_by(LookupReparti.ordine).all()


@router.get("/user-roles", response_model=List[LookupBase])
async def get_ruoli_utente(
    attivo: bool = Query(True),
    db: Session = Depends(get_db)
):
    """Get all user roles"""
    query = db.query(LookupRuoliUtente)
    if attivo is not None:
        query = query.filter(LookupRuoliUtente.attivo == attivo)
    return query.order_by(LookupRuoliUtente.ordine).all()


@router.get("/client-states", response_model=List[ClassificazioneSchema])
async def get_stati_cliente(
    attivo: bool = Query(True),
    db: Session = Depends(get_db)
):
    """Get all client states"""
    query = db.query(LookupStatiCliente)
    if attivo is not None:
        query = query.filter(LookupStatiCliente.attivo == attivo)
    return query.order_by(LookupStatiCliente.ordine).all()


@router.get("/client-classifications", response_model=List[ClassificazioneSchema])
async def get_classificazioni_cliente(
    attivo: bool = Query(True),
    db: Session = Depends(get_db)
):
    """Get all client classifications"""
    query = db.query(LookupClassificazioniCliente)
    if attivo is not None:
        query = query.filter(LookupClassificazioniCliente.attivo == attivo)
    return query.order_by(LookupClassificazioniCliente.ordine).all()
