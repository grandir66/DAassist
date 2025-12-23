from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class CalendarioEvento(BaseModel):
    """Eventi del calendario"""

    __tablename__ = "calendario_eventi"

    titolo = Column(String(200), nullable=False)
    descrizione = Column(Text)
    luogo = Column(String(255))

    data_inizio = Column(DateTime, nullable=False, index=True)
    data_fine = Column(DateTime, nullable=False)

    # Classificazione
    tipo_intervento_id = Column(Integer, ForeignKey("lookup_tipi_intervento.id"), nullable=True)
    cliente_id = Column(Integer, ForeignKey("cache_clienti.id"), nullable=True, index=True)

    # Collegamenti
    richiesta_id = Column(Integer, ForeignKey("richieste_intervento.id", use_alter=True, name="fk_calendario_eventi_richiesta"), nullable=True)
    intervento_id = Column(Integer, ForeignKey("interventi.id", use_alter=True, name="fk_calendario_eventi_intervento"), nullable=True)

    # Tecnico principale
    tecnico_principale_id = Column(Integer, ForeignKey("tecnici.id"), nullable=False, index=True)

    # Stato evento
    stato = Column(String(50), default="PIANIFICATO")  # PIANIFICATO, CONFERMATO, IN_CORSO, COMPLETATO, ANNULLATO

    # Sync calendari esterni
    google_event_id = Column(String(255))
    outlook_event_id = Column(String(255))
    caldav_uid = Column(String(255))

    # Personalizzazione
    colore = Column(String(7))  # Override colore default tipo intervento

    # Promemoria
    promemoria_minuti = Column(Integer, default=30)  # Minuti prima dell'evento

    note = Column(Text)

    # Relationships
    tipo_intervento = relationship("LookupTipiIntervento", lazy="joined")
    cliente = relationship("CacheClienti", lazy="joined")
    richiesta = relationship("RichiestaIntervento")
    intervento = relationship("Intervento", foreign_keys=[intervento_id])
    tecnico_principale = relationship("Tecnico", foreign_keys=[tecnico_principale_id], lazy="joined")

    # Tecnici aggiuntivi
    tecnici = relationship("CalendarioTecnico", back_populates="evento", lazy="dynamic")


class CalendarioTecnico(BaseModel):
    """Assegnazione multipla tecnici ad evento"""

    __tablename__ = "calendario_tecnici"

    evento_id = Column(Integer, ForeignKey("calendario_eventi.id", ondelete="CASCADE"), nullable=False, index=True)
    tecnico_id = Column(Integer, ForeignKey("tecnici.id"), nullable=False, index=True)

    ruolo = Column(String(50))  # PRINCIPALE, SUPPORTO, OSSERVATORE
    confermato = Column(Integer, default=False)
    note = Column(Text)

    # Relationships
    evento = relationship("CalendarioEvento", back_populates="tecnici")
    tecnico = relationship("Tecnico", lazy="joined")


class CalendarioSyncLog(BaseModel):
    """Log sincronizzazione calendari esterni"""

    __tablename__ = "calendario_sync_log"

    tecnico_id = Column(Integer, ForeignKey("tecnici.id"), nullable=False, index=True)
    provider = Column(String(50), nullable=False)  # GOOGLE, OUTLOOK, CALDAV

    direzione = Column(String(20))  # IMPORT, EXPORT
    eventi_sincronizzati = Column(Integer, default=0)
    eventi_errori = Column(Integer, default=0)

    errore = Column(Text)
    dettagli = Column(Text)  # JSON con dettagli

    # Relationships
    tecnico = relationship("Tecnico")
