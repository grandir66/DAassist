from pydantic import BaseModel
from typing import Optional


class LookupBase(BaseModel):
    id: int
    codice: str
    descrizione: str

    class Config:
        from_attributes = True


class CanaleResponse(LookupBase):
    pass


class PrioritaResponse(LookupBase):
    livello: int
    colore: Optional[str]


class StatoTicketResponse(LookupBase):
    colore: Optional[str]
    finale: bool


class StatoInterventoResponse(LookupBase):
    colore: Optional[str]
    finale: bool


class TipoInterventoResponse(LookupBase):
    colore: Optional[str]
    richiede_viaggio: bool


class CategoriaAttivitaResponse(LookupBase):
    prezzo_unitario_default: Optional[float]


class OrigineInterventoResponse(LookupBase):
    pass


class RepartoResponse(LookupBase):
    email: Optional[str]


class RuoloResponse(LookupBase):
    permessi: Optional[str]
