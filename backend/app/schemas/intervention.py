from pydantic import BaseModel, Field
from datetime import datetime, date, time
from typing import Optional
from app.schemas.ticket import ClienteSimple
from app.schemas.lookup import (
    TipoInterventoResponse,
    StatoInterventoResponse,
    OrigineInterventoResponse,
)


# Base schemas
class InterventoBase(BaseModel):
    cliente_id: int
    ticket_id: Optional[int] = None
    tipo_intervento_id: int
    stato_id: int
    origine_id: int
    oggetto: str = Field(..., min_length=1, max_length=200)
    descrizione_lavoro: Optional[str] = None
    note_interne: Optional[str] = None


class InterventoCreate(InterventoBase):
    tecnico_id: int


class InterventoUpdate(BaseModel):
    tipo_intervento_id: Optional[int] = None
    stato_id: Optional[int] = None
    oggetto: Optional[str] = Field(None, min_length=1, max_length=200)
    descrizione_lavoro: Optional[str] = None
    note_interne: Optional[str] = None


class InterventoStartRequest(BaseModel):
    note_avvio: Optional[str] = None


class InterventoCompleteRequest(BaseModel):
    descrizione_lavoro: str = Field(..., min_length=1)
    firma_cliente: Optional[str] = None  # Base64 signature
    firma_nome: Optional[str] = None
    firma_ruolo: Optional[str] = None


# Response schemas
class TecnicoSimple(BaseModel):
    id: int
    nome_completo: str
    email: str

    class Config:
        from_attributes = True


class InterventoResponse(BaseModel):
    id: int
    numero: str
    cliente: Optional[ClienteSimple]
    tecnico: Optional[TecnicoSimple]
    ticket_id: Optional[int]
    tipo_intervento: Optional[TipoInterventoResponse]
    stato: Optional[StatoInterventoResponse]
    origine: Optional[OrigineInterventoResponse]
    oggetto: str
    descrizione_lavoro: Optional[str]
    note_interne: Optional[str]
    data_inizio: Optional[datetime]
    data_fine: Optional[datetime]
    firma_cliente: Optional[str]
    firma_nome: Optional[str]
    firma_ruolo: Optional[str]
    firma_data: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class InterventoListResponse(BaseModel):
    total: int
    page: int
    limit: int
    interventi: list[InterventoResponse]


# Attività intervento
class AttivitaInterventoCreate(BaseModel):
    categoria_id: int
    descrizione: str = Field(..., min_length=1)
    durata: int = Field(..., gt=0)  # minutes
    prezzo_unitario: Optional[float] = None


class AttivitaInterventoResponse(BaseModel):
    id: int
    intervento_id: int
    categoria_id: int
    categoria_descrizione: str
    descrizione: str
    durata: int
    prezzo_unitario: Optional[float]
    totale: Optional[float]
    created_at: datetime

    class Config:
        from_attributes = True


# Sessioni Lavoro (Tempi)
class SessioneCreate(BaseModel):
    data: date
    ora_inizio: time
    ora_fine: Optional[time] = None
    tipo_intervento_id: int
    km_percorsi: Optional[float] = Field(None, ge=0)
    tempo_viaggio_minuti: Optional[int] = Field(None, ge=0)
    note: Optional[str] = None


class SessioneUpdate(BaseModel):
    data: Optional[date] = None
    ora_inizio: Optional[time] = None
    ora_fine: Optional[time] = None
    tipo_intervento_id: Optional[int] = None
    km_percorsi: Optional[float] = Field(None, ge=0)
    tempo_viaggio_minuti: Optional[int] = Field(None, ge=0)
    note: Optional[str] = None


class SessioneResponse(BaseModel):
    id: int
    intervento_id: int
    tecnico: TecnicoSimple
    data: date
    ora_inizio: time
    ora_fine: Optional[time]
    durata_minuti: Optional[int]
    tipo_intervento: TipoInterventoResponse
    km_percorsi: Optional[float]
    tempo_viaggio_minuti: Optional[int]
    note: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# Righe Attività (Update/Delete)
class RigaAttivitaUpdate(BaseModel):
    categoria_id: Optional[int] = None
    descrizione: Optional[str] = Field(None, min_length=1)
    quantita: Optional[float] = Field(None, gt=0)
    prezzo_unitario: Optional[float] = Field(None, ge=0)
    sconto_percentuale: Optional[float] = Field(None, ge=0, le=100)
    fatturabile: Optional[bool] = None
    in_garanzia: Optional[bool] = None
    incluso_contratto: Optional[bool] = None


class RigaAttivitaResponse(BaseModel):
    id: int
    intervento_id: int
    numero_riga: int
    categoria_id: int
    descrizione: str
    quantita: float
    unita_misura: str
    prezzo_unitario: float
    sconto_percentuale: float
    fatturabile: bool
    in_garanzia: bool
    incluso_contratto: bool
    importo: float
    created_at: datetime

    class Config:
        from_attributes = True
