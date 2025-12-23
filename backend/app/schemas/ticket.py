from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


# Base schemas
class TicketBase(BaseModel):
    oggetto: str = Field(..., min_length=1, max_length=200)
    descrizione: Optional[str] = None
    cliente_id: int
    referente_id: Optional[int] = None
    referente_nome: Optional[str] = None
    canale_id: int
    priorita_id: int
    contratto_id: Optional[int] = None
    asset_id: Optional[int] = None


class TicketCreate(TicketBase):
    pass


class TicketUpdate(BaseModel):
    oggetto: Optional[str] = Field(None, min_length=1, max_length=200)
    descrizione: Optional[str] = None
    priorita_id: Optional[int] = None
    tecnico_assegnato_id: Optional[int] = None
    stato_id: Optional[int] = None


# Response schemas
class ClienteSimple(BaseModel):
    id: int
    codice_gestionale: str
    ragione_sociale: str

    class Config:
        from_attributes = True


class ReferenteSimple(BaseModel):
    id: int
    nome: str
    cognome: str
    email: Optional[str] = None

    class Config:
        from_attributes = True


class TecnicoSimple(BaseModel):
    id: int
    username: str
    nome: str
    cognome: str
    email: str

    class Config:
        from_attributes = True


class LookupSimple(BaseModel):
    id: int
    codice: str
    descrizione: str

    class Config:
        from_attributes = True


class PrioritaResponse(LookupSimple):
    livello: int
    colore: str


class StatoTicketResponse(LookupSimple):
    colore: str
    finale: bool


class TicketResponse(BaseModel):
    id: int
    numero: str
    oggetto: str
    descrizione: Optional[str] = None

    # Cliente e referente
    cliente_id: int
    cliente: Optional[ClienteSimple] = None
    referente_id: Optional[int] = None
    referente: Optional[ReferenteSimple] = None
    referente_nome: Optional[str] = None

    # Classificazione
    canale_id: int
    canale: Optional[LookupSimple] = None
    priorita_id: int
    priorita: Optional[PrioritaResponse] = None
    stato_id: int
    stato: Optional[StatoTicketResponse] = None

    # Assegnazione
    tecnico_assegnato_id: Optional[int] = None
    tecnico_assegnato: Optional[TecnicoSimple] = None

    # SLA
    sla_scadenza_risposta: Optional[datetime] = None
    sla_scadenza_risoluzione: Optional[datetime] = None
    sla_prima_risposta_at: Optional[datetime] = None

    # Chiusura
    data_chiusura: Optional[datetime] = None
    tipo_chiusura: Optional[str] = None

    # Timestamps
    created_at: datetime
    updated_at: datetime
    attivo: bool

    class Config:
        from_attributes = True


class TicketListResponse(BaseModel):
    total: int
    page: int
    limit: int
    tickets: list[TicketResponse]


# Action schemas
class TicketAssignRequest(BaseModel):
    tecnico_id: int


class TicketCloseRequest(BaseModel):
    tipo_chiusura: str = Field(..., pattern="^(DIRETTA|INTERVENTO_IMMEDIATO|RICHIESTA_INTERVENTO)$")
    note_chiusura: str


class TicketNoteCreate(BaseModel):
    nota: str


class TicketMessaggioCreate(BaseModel):
    messaggio: str
