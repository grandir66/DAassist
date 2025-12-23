from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional


class DashboardTicketStats(BaseModel):
    """Statistics for tickets"""
    totali: int
    aperti: int
    nuovi: int
    in_lavorazione: int
    chiusi_oggi: int
    chiusi_settimana: int
    chiusi_mese: int


class DashboardInterventoStats(BaseModel):
    """Statistics for interventions"""
    totali: int
    pianificati: int
    in_corso: int
    completati_oggi: int
    completati_settimana: int
    completati_mese: int


class InterventoOggi(BaseModel):
    """Intervention scheduled for today"""
    id: int
    numero: str
    cliente_ragione_sociale: str
    oggetto: str
    tipo_descrizione: str
    tipo_richiede_viaggio: bool
    stato_codice: str
    stato_descrizione: str
    data_inizio: Optional[datetime]

    class Config:
        from_attributes = True


class TicketRecente(BaseModel):
    """Recent ticket"""
    id: int
    numero: str
    cliente_ragione_sociale: Optional[str]
    oggetto: str
    priorita_codice: str
    priorita_descrizione: str
    stato_codice: str
    stato_descrizione: str
    created_at: datetime

    class Config:
        from_attributes = True


class DashboardResponse(BaseModel):
    """Dashboard aggregated data response"""
    ticket_stats: DashboardTicketStats
    intervento_stats: DashboardInterventoStats
    recent_tickets: List[TicketRecente]
    interventi_oggi: List[InterventoOggi]
