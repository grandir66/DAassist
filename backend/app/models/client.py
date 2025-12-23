from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Text, Numeric, Date
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class CacheClienti(BaseModel):
    """Cache locale dei clienti dal gestionale"""

    __tablename__ = "cache_clienti"

    codice_gestionale = Column(String(50), unique=True, nullable=False, index=True)
    ragione_sociale = Column(String(255), nullable=False, index=True)
    partita_iva = Column(String(20))
    codice_fiscale = Column(String(20))

    # Indirizzo sede legale
    indirizzo = Column(String(255))
    cap = Column(String(10))
    citta = Column(String(100))
    provincia = Column(String(2))
    nazione = Column(String(50), default="IT")

    # Contatti
    telefono = Column(String(50))
    email = Column(String(255))
    pec = Column(String(255))
    sito_web = Column(String(255))

    # Gestione cliente
    stato_cliente = Column(String(20), default="ATTIVO", index=True)  # ATTIVO, SOSPESO, INATTIVO
    classificazione = Column(String(50))  # VIP, STANDARD, BASIC, etc.
    referente_it_id = Column(Integer, ForeignKey("cache_referenti.id"), nullable=True)  # Referente IT principale

    # Orari di servizio (JSON format)
    orari_servizio = Column(Text)  # JSON: {"lunedi": "08:00-18:00", ...}

    # Nomi alternativi per ricerca (separati da virgola)
    nomi_alternativi = Column(Text)  # Es: "Acronimo SPA, Nome Breve"

    # Sync
    ultimo_sync = Column(DateTime, nullable=False)
    hash_dati = Column(String(64))  # SHA256 per rilevare modifiche

    # Note
    note = Column(Text)

    # Relationships
    referente_it = relationship("CacheReferenti", foreign_keys=[referente_it_id], lazy="joined", post_update=True)


class CacheContratti(BaseModel):
    """Cache locale dei contratti dal gestionale"""

    __tablename__ = "cache_contratti"

    codice_gestionale = Column(String(50), unique=True, nullable=False, index=True)
    cliente_id = Column(Integer, ForeignKey("cache_clienti.id"), nullable=False, index=True)

    descrizione = Column(String(255), nullable=False)
    tipo_contratto = Column(String(100))  # Assistenza, Manutenzione, Canone, etc.

    # Validità
    data_inizio = Column(Date, nullable=False)
    data_fine = Column(Date)
    attivo_gestionale = Column(Integer, default=True)

    # Budget
    ore_incluse = Column(Numeric(10, 2))
    ore_utilizzate = Column(Numeric(10, 2), default=0.00)
    importo_annuo = Column(Numeric(10, 2))

    # SLA associato
    sla_id = Column(Integer, ForeignKey("sla_definizioni.id"), nullable=True)

    # Sync
    ultimo_sync = Column(DateTime, nullable=False)
    hash_dati = Column(String(64))

    # Relationships
    cliente = relationship("CacheClienti", lazy="joined")
    sla = relationship("SLADefinizione", lazy="joined")


class SediCliente(BaseModel):
    """Sedi operative del cliente (diverse dalla sede legale)"""

    __tablename__ = "sedi_cliente"

    cliente_id = Column(Integer, ForeignKey("cache_clienti.id"), nullable=False, index=True)

    # Identificazione sede
    nome_sede = Column(String(100), nullable=False)  # Es: "Sede Milano", "Filiale Roma"
    codice_sede = Column(String(50))  # Codice interno cliente

    # Indirizzo
    indirizzo = Column(String(255), nullable=False)
    cap = Column(String(10))
    citta = Column(String(100), nullable=False)
    provincia = Column(String(2))
    nazione = Column(String(50), default="IT")

    # Contatti sede
    telefono = Column(String(50))
    email = Column(String(255))

    # Orari specifici sede (se diversi da quelli generali)
    orari_servizio = Column(Text)  # JSON format

    # Note
    note = Column(Text)

    # Relationships
    cliente = relationship("CacheClienti", backref="sedi", lazy="joined")


class CacheReferenti(BaseModel):
    """Cache locale dei referenti clienti - Rubrica contatti"""

    __tablename__ = "cache_referenti"

    codice_gestionale = Column(String(50), unique=True, nullable=True, index=True)
    cliente_id = Column(Integer, ForeignKey("cache_clienti.id"), nullable=False, index=True)
    sede_id = Column(Integer, ForeignKey("sedi_cliente.id"), nullable=True)  # Sede di appartenenza

    nome = Column(String(100), nullable=False, index=True)
    cognome = Column(String(100), nullable=False, index=True)
    ruolo = Column(String(100))  # IT Manager, Amministratore, Responsabile, etc.

    # Contatti
    telefono = Column(String(50))
    cellulare = Column(String(50))
    interno_telefonico = Column(String(20))  # Interno centralino
    email = Column(String(255), index=True)

    # Preferenze
    contatto_principale = Column(Integer, default=0)
    riceve_notifiche = Column(Integer, default=1)
    referente_it = Column(Integer, default=0)  # Flag per referente IT

    # Note
    note = Column(Text)

    # Sync
    ultimo_sync = Column(DateTime, nullable=False)
    hash_dati = Column(String(64))

    # Relationships
    cliente = relationship("CacheClienti", foreign_keys=[cliente_id], backref="referenti", lazy="joined")
    sede = relationship("SediCliente", lazy="joined")

    @property
    def nome_completo(self) -> str:
        return f"{self.nome} {self.cognome}"


class SLADefinizione(BaseModel):
    """Definizioni SLA"""

    __tablename__ = "sla_definizioni"

    nome = Column(String(100), nullable=False, unique=True)
    descrizione = Column(Text)

    # Tempi di risposta (minuti) per priorità
    tempo_risposta_critica = Column(Integer, default=60)  # 1 ora
    tempo_risposta_urgente = Column(Integer, default=120)  # 2 ore
    tempo_risposta_alta = Column(Integer, default=240)  # 4 ore
    tempo_risposta_normale = Column(Integer, default=480)  # 8 ore
    tempo_risposta_bassa = Column(Integer, default=1440)  # 24 ore

    # Tempi di risoluzione (minuti) per priorità
    tempo_risoluzione_critica = Column(Integer, default=240)  # 4 ore
    tempo_risoluzione_urgente = Column(Integer, default=480)  # 8 ore
    tempo_risoluzione_alta = Column(Integer, default=960)  # 16 ore
    tempo_risoluzione_normale = Column(Integer, default=1440)  # 24 ore
    tempo_risoluzione_bassa = Column(Integer, default=4320)  # 72 ore

    # Finestre orarie lavorative
    ora_inizio_lavorativa = Column(String(5), default="08:00")
    ora_fine_lavorativa = Column(String(5), default="18:00")

    # Giorni lavorativi (JSON: [1,2,3,4,5] per Lun-Ven)
    giorni_lavorativi = Column(String(50), default="[1,2,3,4,5]")

    # Include festivi
    include_festivi = Column(Integer, default=False)
