from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


# Cliente schemas
class ClienteBase(BaseModel):
    codice_gestionale: str = Field(..., min_length=1, max_length=50)
    ragione_sociale: str = Field(..., min_length=1, max_length=255)
    partita_iva: Optional[str] = Field(None, max_length=20)
    codice_fiscale: Optional[str] = Field(None, max_length=20)
    indirizzo: Optional[str] = Field(None, max_length=255)
    cap: Optional[str] = Field(None, max_length=10)
    citta: Optional[str] = Field(None, max_length=100)
    provincia: Optional[str] = Field(None, max_length=2)
    nazione: str = Field(default="IT", max_length=50)
    telefono: Optional[str] = Field(None, max_length=50)
    email: Optional[str] = Field(None, max_length=255)
    pec: Optional[str] = Field(None, max_length=255)
    sito_web: Optional[str] = Field(None, max_length=255)
    stato_cliente: str = Field(default="ATTIVO", max_length=20)
    classificazione: Optional[str] = Field(None, max_length=50)
    referente_it_id: Optional[int] = None
    orari_servizio: Optional[str] = None
    nomi_alternativi: Optional[str] = None
    note: Optional[str] = None


class ReferenteITInfo(BaseModel):
    id: int
    nome: str
    cognome: str
    email: Optional[str]
    cellulare: Optional[str]

    class Config:
        from_attributes = True


class ClienteResponse(BaseModel):
    id: int
    codice_gestionale: str
    ragione_sociale: str
    partita_iva: Optional[str]
    codice_fiscale: Optional[str]
    indirizzo: Optional[str]
    cap: Optional[str]
    citta: Optional[str]
    provincia: Optional[str]
    nazione: str
    telefono: Optional[str]
    email: Optional[str]
    pec: Optional[str]
    sito_web: Optional[str]
    stato_cliente: str
    classificazione: Optional[str]
    referente_it_id: Optional[int]
    referente_it: Optional[ReferenteITInfo]
    orari_servizio: Optional[str]
    nomi_alternativi: Optional[str]
    note: Optional[str]
    ultimo_sync: datetime
    created_at: datetime
    updated_at: Optional[datetime]
    attivo: bool

    class Config:
        from_attributes = True


class ClienteListResponse(BaseModel):
    total: int
    page: int
    limit: int
    clienti: list[ClienteResponse]


# Contratto schemas
class ContrattoResponse(BaseModel):
    id: int
    cliente_id: int
    codice_gestionale: str
    descrizione: str
    data_inizio: Optional[datetime]
    data_fine: Optional[datetime]
    ore_incluse: Optional[float]
    ore_utilizzate: float
    attivo: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Sede Cliente schemas
class SedeClienteBase(BaseModel):
    cliente_id: int
    nome_sede: str = Field(..., min_length=1, max_length=100)
    codice_sede: Optional[str] = Field(None, max_length=50)
    indirizzo: str = Field(..., min_length=1, max_length=255)
    cap: Optional[str] = Field(None, max_length=10)
    citta: str = Field(..., min_length=1, max_length=100)
    provincia: Optional[str] = Field(None, max_length=2)
    nazione: str = Field(default="IT", max_length=50)
    telefono: Optional[str] = Field(None, max_length=50)
    email: Optional[str] = Field(None, max_length=255)
    orari_servizio: Optional[str] = None
    note: Optional[str] = None


class SedeClienteCreate(SedeClienteBase):
    pass


class SedeClienteUpdate(BaseModel):
    nome_sede: Optional[str] = Field(None, min_length=1, max_length=100)
    codice_sede: Optional[str] = Field(None, max_length=50)
    indirizzo: Optional[str] = Field(None, min_length=1, max_length=255)
    cap: Optional[str] = Field(None, max_length=10)
    citta: Optional[str] = Field(None, min_length=1, max_length=100)
    provincia: Optional[str] = Field(None, max_length=2)
    nazione: Optional[str] = Field(None, max_length=50)
    telefono: Optional[str] = Field(None, max_length=50)
    email: Optional[str] = Field(None, max_length=255)
    orari_servizio: Optional[str] = None
    note: Optional[str] = None
    attivo: Optional[bool] = None


class SedeClienteResponse(BaseModel):
    id: int
    cliente_id: int
    nome_sede: str
    codice_sede: Optional[str]
    indirizzo: str
    cap: Optional[str]
    citta: str
    provincia: Optional[str]
    nazione: str
    telefono: Optional[str]
    email: Optional[str]
    orari_servizio: Optional[str]
    note: Optional[str]
    attivo: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# Referente schemas
class ReferenteBase(BaseModel):
    cliente_id: int
    sede_id: Optional[int] = None
    nome: str = Field(..., min_length=1, max_length=100)
    cognome: str = Field(..., min_length=1, max_length=100)
    ruolo: Optional[str] = Field(None, max_length=100)
    telefono: Optional[str] = Field(None, max_length=50)
    cellulare: Optional[str] = Field(None, max_length=50)
    interno_telefonico: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=255)
    contatto_principale: bool = False
    riceve_notifiche: bool = True
    referente_it: bool = False
    note: Optional[str] = None


class ReferenteCreate(ReferenteBase):
    codice_gestionale: Optional[str] = Field(None, max_length=50)


class ReferenteUpdate(BaseModel):
    sede_id: Optional[int] = None
    nome: Optional[str] = Field(None, min_length=1, max_length=100)
    cognome: Optional[str] = Field(None, min_length=1, max_length=100)
    ruolo: Optional[str] = Field(None, max_length=100)
    telefono: Optional[str] = Field(None, max_length=50)
    cellulare: Optional[str] = Field(None, max_length=50)
    interno_telefonico: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=255)
    contatto_principale: Optional[bool] = None
    riceve_notifiche: Optional[bool] = None
    referente_it: Optional[bool] = None
    note: Optional[str] = None
    attivo: Optional[bool] = None


class SedeInfo(BaseModel):
    id: int
    nome_sede: str
    citta: str

    class Config:
        from_attributes = True


class ReferenteResponse(BaseModel):
    id: int
    cliente_id: int
    sede_id: Optional[int]
    sede: Optional[SedeInfo]
    nome: str
    cognome: str
    ruolo: Optional[str]
    telefono: Optional[str]
    cellulare: Optional[str]
    interno_telefonico: Optional[str]
    email: Optional[str]
    contatto_principale: bool
    riceve_notifiche: bool
    referente_it: bool
    note: Optional[str]
    attivo: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class ClienteDetailResponse(ClienteResponse):
    contratti: list[ContrattoResponse] = []
    referenti: list[ReferenteResponse] = []
    sedi: list[SedeClienteResponse] = []

    class Config:
        from_attributes = True
