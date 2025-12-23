from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Text, Numeric, Date, Time
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Intervento(BaseModel):
    """Interventi tecnici"""

    __tablename__ = "interventi"

    numero = Column(String(50), unique=True, nullable=False, index=True)
    serie = Column(String(20))  # Per numerazione gestionale

    # Origine
    origine_id = Column(Integer, ForeignKey("lookup_origini_intervento.id"), nullable=False)
    ticket_id = Column(Integer, ForeignKey("ticket.id"), nullable=True, index=True)
    richiesta_id = Column(Integer, ForeignKey("richieste_intervento.id", use_alter=True, name="fk_intervento_richiesta"), nullable=True)
    evento_calendario_id = Column(Integer, ForeignKey("calendario_eventi.id", use_alter=True, name="fk_intervento_calendario"), nullable=True)

    # Cliente
    cliente_id = Column(Integer, ForeignKey("cache_clienti.id"), nullable=False, index=True)
    contratto_id = Column(Integer, ForeignKey("cache_contratti.id"), nullable=True)

    # Classificazione
    tipo_intervento_id = Column(Integer, ForeignKey("lookup_tipi_intervento.id"), nullable=False)
    stato_id = Column(Integer, ForeignKey("lookup_stati_intervento.id"), nullable=False, index=True)

    # Tecnico principale
    tecnico_id = Column(Integer, ForeignKey("tecnici.id"), nullable=False, index=True)

    # Descrizione
    oggetto = Column(String(200), nullable=False)
    descrizione_lavoro = Column(Text)
    note_interne = Column(Text)

    # Date
    data_inizio = Column(DateTime)
    data_fine = Column(DateTime)

    # Firma cliente
    firma_cliente = Column(Text)  # Base64
    firma_nome = Column(String(200))
    firma_ruolo = Column(String(100))
    firma_data = Column(DateTime)

    # Sincronizzazione gestionale
    sincronizzato_gestionale = Column(Integer, default=0, index=True)
    codice_gestionale = Column(String(50))
    data_sincronizzazione = Column(DateTime)
    errore_sincronizzazione = Column(Text)

    # Relationships
    origine = relationship("LookupOriginiIntervento", lazy="joined")
    ticket = relationship("Ticket")
    richiesta = relationship("RichiestaIntervento")
    evento_calendario = relationship("CalendarioEvento", foreign_keys=[evento_calendario_id])
    cliente = relationship("CacheClienti", lazy="joined")
    contratto = relationship("CacheContratti")
    tipo_intervento = relationship("LookupTipiIntervento", lazy="joined")
    stato = relationship("LookupStatiIntervento", lazy="joined")
    tecnico = relationship("Tecnico", lazy="joined")

    # One-to-many
    righe = relationship("InterventoRiga", back_populates="intervento", lazy="dynamic")
    sessioni = relationship("InterventoSessione", back_populates="intervento", lazy="dynamic")
    tecnici_team = relationship("InterventoTecnico", back_populates="intervento", lazy="dynamic")
    allegati = relationship("InterventoAllegato", back_populates="intervento", lazy="dynamic")


class InterventoRiga(BaseModel):
    """Righe attività intervento"""

    __tablename__ = "interventi_righe"

    intervento_id = Column(Integer, ForeignKey("interventi.id", ondelete="CASCADE"), nullable=False, index=True)
    numero_riga = Column(Integer, nullable=False)

    categoria_id = Column(Integer, ForeignKey("lookup_categorie_attivita.id"), nullable=False)
    descrizione = Column(Text, nullable=False)

    quantita = Column(Numeric(10, 2), default=1.00)
    unita_misura = Column(String(20), default="ore")
    prezzo_unitario = Column(Numeric(10, 2), default=0.00)
    sconto_percentuale = Column(Numeric(5, 2), default=0.00)

    # Flag
    fatturabile = Column(Integer, default=True)
    in_garanzia = Column(Integer, default=False)
    incluso_contratto = Column(Integer, default=False)

    # Collegamento a sessione (opzionale)
    sessione_id = Column(Integer, ForeignKey("interventi_sessioni.id"), nullable=True)

    # Relationships
    intervento = relationship("Intervento", back_populates="righe")
    categoria = relationship("LookupCategorieAttivita", lazy="joined")
    sessione = relationship("InterventoSessione", foreign_keys=[sessione_id])

    @property
    def importo(self) -> float:
        base = float(self.quantita * self.prezzo_unitario)
        sconto = base * (float(self.sconto_percentuale) / 100)
        return base - sconto


class InterventoSessione(BaseModel):
    """Sessioni di lavoro (tempi)"""

    __tablename__ = "interventi_sessioni"

    intervento_id = Column(Integer, ForeignKey("interventi.id", ondelete="CASCADE"), nullable=False, index=True)
    tecnico_id = Column(Integer, ForeignKey("tecnici.id"), nullable=False)

    data = Column(Date, nullable=False)
    ora_inizio = Column(Time)
    ora_fine = Column(Time)
    durata_minuti = Column(Integer)  # Calcolata o manuale

    tipo_intervento_id = Column(Integer, ForeignKey("lookup_tipi_intervento.id"), nullable=False)

    # Viaggio
    km_percorsi = Column(Numeric(10, 2))
    tempo_viaggio_minuti = Column(Integer)

    # Geolocalizzazione (opzionale)
    latitudine_inizio = Column(Numeric(10, 6))
    longitudine_inizio = Column(Numeric(10, 6))
    latitudine_fine = Column(Numeric(10, 6))
    longitudine_fine = Column(Numeric(10, 6))

    note = Column(Text)

    # Relationships
    intervento = relationship("Intervento", back_populates="sessioni")
    tecnico = relationship("Tecnico")
    tipo_intervento = relationship("LookupTipiIntervento", lazy="joined")


class InterventoTecnico(BaseModel):
    """Tecnici aggiuntivi nel team"""

    __tablename__ = "interventi_tecnici"

    intervento_id = Column(Integer, ForeignKey("interventi.id", ondelete="CASCADE"), nullable=False, index=True)
    tecnico_id = Column(Integer, ForeignKey("tecnici.id"), nullable=False)

    ruolo = Column(String(50))  # PRINCIPALE, SUPPORTO, FORMAZIONE
    ore_lavorate = Column(Numeric(10, 2))
    note = Column(Text)

    # Relationships
    intervento = relationship("Intervento", back_populates="tecnici_team")
    tecnico = relationship("Tecnico", lazy="joined")


class InterventoAllegato(BaseModel):
    """Allegati intervento (foto, documenti, etc.)"""

    __tablename__ = "interventi_allegati"

    intervento_id = Column(Integer, ForeignKey("interventi.id", ondelete="CASCADE"), nullable=False, index=True)
    tecnico_id = Column(Integer, ForeignKey("tecnici.id"), nullable=True)

    tipo = Column(String(20))  # FOTO, DOCUMENTO, FIRMA, SCREENSHOT
    nome_file = Column(String(255), nullable=False)
    nome_originale = Column(String(255), nullable=False)
    percorso = Column(String(500), nullable=False)
    mime_type = Column(String(100))
    dimensione = Column(Integer)

    descrizione = Column(Text)

    # Relationships
    intervento = relationship("Intervento", back_populates="allegati")
    tecnico = relationship("Tecnico")


class RichiestaIntervento(BaseModel):
    """Richieste di intervento da pianificare"""

    __tablename__ = "richieste_intervento"

    ticket_id = Column(Integer, ForeignKey("ticket.id"), nullable=True, index=True)
    cliente_id = Column(Integer, ForeignKey("cache_clienti.id"), nullable=False, index=True)

    oggetto = Column(String(200), nullable=False)
    descrizione = Column(Text)
    priorita_id = Column(Integer, ForeignKey("lookup_priorita.id"), nullable=False)

    stato = Column(String(50), default="PENDENTE", index=True)  # PENDENTE, PIANIFICATA, COMPLETATA

    # Data richiesta / preferita
    data_richiesta = Column(DateTime, nullable=False)
    data_preferita = Column(DateTime)

    # Assegnazione
    tecnico_richiesto_id = Column(Integer, ForeignKey("tecnici.id"), nullable=True)
    tipo_intervento_id = Column(Integer, ForeignKey("lookup_tipi_intervento.id"), nullable=True)

    note = Column(Text)

    # Relationships
    ticket = relationship("Ticket")
    cliente = relationship("CacheClienti", lazy="joined")
    priorita = relationship("LookupPriorita", lazy="joined")
    tecnico_richiesto = relationship("Tecnico")
    tipo_intervento = relationship("LookupTipiIntervento")
