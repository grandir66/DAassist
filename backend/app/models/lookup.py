from sqlalchemy import Column, String, Integer, Numeric
from app.models.base import BaseModel


class LookupCanaliRichiesta(BaseModel):
    """Canali di richiesta ticket (Telefono, Email, WebApp, etc.)"""

    __tablename__ = "lookup_canali_richiesta"

    codice = Column(String(50), unique=True, nullable=False, index=True)
    descrizione = Column(String(200), nullable=False)
    ordine = Column(Integer, default=0)


class LookupPriorita(BaseModel):
    """Priorità ticket (Critica, Urgente, Alta, Normale, Bassa)"""

    __tablename__ = "lookup_priorita"

    codice = Column(String(50), unique=True, nullable=False, index=True)
    descrizione = Column(String(200), nullable=False)
    livello = Column(Integer, nullable=False)  # 1=Critica, 5=Bassa
    colore = Column(String(7), default="#6B7280")  # Hex color
    ordine = Column(Integer, default=0)


class LookupStatiTicket(BaseModel):
    """Stati possibili per i ticket"""

    __tablename__ = "lookup_stati_ticket"

    codice = Column(String(50), unique=True, nullable=False, index=True)
    descrizione = Column(String(200), nullable=False)
    colore = Column(String(7), default="#6B7280")
    ordine = Column(Integer, default=0)
    finale = Column(Integer, default=False)  # Stato finale (chiuso/annullato)


class LookupStatiIntervento(BaseModel):
    """Stati possibili per gli interventi"""

    __tablename__ = "lookup_stati_intervento"

    codice = Column(String(50), unique=True, nullable=False, index=True)
    descrizione = Column(String(200), nullable=False)
    colore = Column(String(7), default="#6B7280")
    ordine = Column(Integer, default=0)
    finale = Column(Integer, default=False)


class LookupTipiIntervento(BaseModel):
    """Tipi di intervento (Cliente, Laboratorio, Remoto, Telefonico)"""

    __tablename__ = "lookup_tipi_intervento"

    codice = Column(String(50), unique=True, nullable=False, index=True)
    descrizione = Column(String(200), nullable=False)
    colore = Column(String(7), default="#3B82F6")
    richiede_viaggio = Column(Integer, default=False)
    ordine = Column(Integer, default=0)


class LookupCategorieAttivita(BaseModel):
    """Categorie attività (Tecnica, Sistemistica, Gestionale, etc.)"""

    __tablename__ = "lookup_categorie_attivita"

    codice = Column(String(50), unique=True, nullable=False, index=True)
    descrizione = Column(String(200), nullable=False)
    prezzo_unitario_default = Column(Numeric(10, 2), default=0.00)
    ordine = Column(Integer, default=0)


class LookupOriginiIntervento(BaseModel):
    """Origini intervento (Da Ticket, Da Pianificazione, Spontaneo, etc.)"""

    __tablename__ = "lookup_origini_intervento"

    codice = Column(String(50), unique=True, nullable=False, index=True)
    descrizione = Column(String(200), nullable=False)
    ordine = Column(Integer, default=0)


class LookupReparti(BaseModel):
    """Reparti aziendali"""

    __tablename__ = "lookup_reparti"

    codice = Column(String(50), unique=True, nullable=False, index=True)
    descrizione = Column(String(200), nullable=False)
    email = Column(String(255))
    ordine = Column(Integer, default=0)


class LookupRuoliUtente(BaseModel):
    """Ruoli utente (Admin, Tecnico, Operatore, Cliente)"""

    __tablename__ = "lookup_ruoli_utente"

    codice = Column(String(50), unique=True, nullable=False, index=True)
    descrizione = Column(String(200), nullable=False)
    permessi = Column(String)  # JSON array di permessi
    ordine = Column(Integer, default=0)


class LookupStatiCliente(BaseModel):
    """Stati cliente (Attivo, Sospeso, Inattivo)"""

    __tablename__ = "lookup_stati_cliente"

    codice = Column(String(50), unique=True, nullable=False, index=True)
    descrizione = Column(String(200), nullable=False)
    colore = Column(String(7), default="#6B7280")
    ordine = Column(Integer, default=0)


class LookupClassificazioniCliente(BaseModel):
    """Classificazioni cliente (VIP, Standard, Basic, etc.)"""

    __tablename__ = "lookup_classificazioni_cliente"

    codice = Column(String(50), unique=True, nullable=False, index=True)
    descrizione = Column(String(200), nullable=False)
    colore = Column(String(7), default="#6B7280")
    ordine = Column(Integer, default=0)
