from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Ticket(BaseModel):
    """Ticket di assistenza"""

    __tablename__ = "ticket"

    numero = Column(String(50), unique=True, nullable=False, index=True)

    # Cliente e referente
    cliente_id = Column(Integer, ForeignKey("cache_clienti.id"), nullable=False, index=True)
    referente_id = Column(Integer, ForeignKey("cache_referenti.id"), nullable=True)
    referente_nome = Column(String(200))  # Se referente non in anagrafica

    # Classificazione
    canale_id = Column(Integer, ForeignKey("lookup_canali_richiesta.id"), nullable=False)
    priorita_id = Column(Integer, ForeignKey("lookup_priorita.id"), nullable=False)
    stato_id = Column(Integer, ForeignKey("lookup_stati_ticket.id"), nullable=False, index=True)

    # Descrizione
    oggetto = Column(String(200), nullable=False)
    descrizione = Column(Text)

    # Assegnazione
    tecnico_assegnato_id = Column(Integer, ForeignKey("tecnici.id"), nullable=True, index=True)
    reparto_id = Column(Integer, ForeignKey("lookup_reparti.id"), nullable=True)

    # Contratto e asset
    contratto_id = Column(Integer, ForeignKey("cache_contratti.id"), nullable=True)
    asset_id = Column(Integer, ForeignKey("asset.id"), nullable=True)

    # SLA tracking
    sla_scadenza_risposta = Column(DateTime)
    sla_scadenza_risoluzione = Column(DateTime)
    sla_prima_risposta_at = Column(DateTime)
    sla_paused_at = Column(DateTime)  # Quando messo in pausa (attesa cliente)
    sla_paused_total_minutes = Column(Integer, default=0)  # Tempo totale in pausa

    # Chiusura
    data_chiusura = Column(DateTime)
    tipo_chiusura = Column(String(50))  # DIRETTA, INTERVENTO_IMMEDIATO, RICHIESTA_INTERVENTO
    note_chiusura = Column(Text)
    chiuso_da_id = Column(Integer, ForeignKey("tecnici.id"), nullable=True)

    # Knowledge base
    kb_articolo_id = Column(Integer, ForeignKey("kb_articoli.id"), nullable=True)

    # Relationships
    cliente = relationship("CacheClienti", lazy="joined")
    referente = relationship("CacheReferenti", lazy="joined")
    canale = relationship("LookupCanaliRichiesta", lazy="joined")
    priorita = relationship("LookupPriorita", lazy="joined")
    stato = relationship("LookupStatiTicket", lazy="joined")
    tecnico_assegnato = relationship("Tecnico", foreign_keys=[tecnico_assegnato_id], lazy="joined")
    chiuso_da = relationship("Tecnico", foreign_keys=[chiuso_da_id])
    contratto = relationship("CacheContratti", lazy="joined")
    asset = relationship("Asset")
    reparto = relationship("LookupReparti")
    kb_articolo = relationship("KBArticolo")

    # Notes, messages, attachments (one-to-many)
    note = relationship("TicketNota", back_populates="ticket", lazy="dynamic")
    messaggi = relationship("TicketMessaggio", back_populates="ticket", lazy="dynamic")
    allegati = relationship("TicketAllegato", back_populates="ticket", lazy="dynamic")


class TicketNota(BaseModel):
    """Note interne del ticket (non visibili al cliente)"""

    __tablename__ = "ticket_note"

    ticket_id = Column(Integer, ForeignKey("ticket.id", ondelete="CASCADE"), nullable=False, index=True)
    tecnico_id = Column(Integer, ForeignKey("tecnici.id"), nullable=False)
    nota = Column(Text, nullable=False)

    # Relationships
    ticket = relationship("Ticket", back_populates="note")
    tecnico = relationship("Tecnico", lazy="joined")


class TicketMessaggio(BaseModel):
    """Messaggi ticket (comunicazione cliente-tecnico, visibili su portale)"""

    __tablename__ = "ticket_messaggi"

    ticket_id = Column(Integer, ForeignKey("ticket.id", ondelete="CASCADE"), nullable=False, index=True)
    mittente_tipo = Column(String(20), nullable=False)  # TECNICO, CLIENTE
    mittente_tecnico_id = Column(Integer, ForeignKey("tecnici.id"), nullable=True)
    mittente_cliente_id = Column(Integer, ForeignKey("clienti_portale.id"), nullable=True)
    mittente_nome = Column(String(200))  # Se mittente senza account

    messaggio = Column(Text, nullable=False)
    letto = Column(Integer, default=False)
    letto_at = Column(DateTime)

    # Relationships
    ticket = relationship("Ticket", back_populates="messaggi")
    mittente_tecnico = relationship("Tecnico")
    mittente_cliente = relationship("ClientePortale")


class TicketAllegato(BaseModel):
    """Allegati del ticket"""

    __tablename__ = "ticket_allegati"

    ticket_id = Column(Integer, ForeignKey("ticket.id", ondelete="CASCADE"), nullable=False, index=True)
    tecnico_id = Column(Integer, ForeignKey("tecnici.id"), nullable=True)

    nome_file = Column(String(255), nullable=False)
    nome_originale = Column(String(255), nullable=False)
    percorso = Column(String(500), nullable=False)
    mime_type = Column(String(100))
    dimensione = Column(Integer)  # bytes

    # Relationships
    ticket = relationship("Ticket", back_populates="allegati")
    tecnico = relationship("Tecnico")


class TicketStorico(BaseModel):
    """Storico modifiche ticket (audit log)"""

    __tablename__ = "ticket_storico"

    ticket_id = Column(Integer, ForeignKey("ticket.id", ondelete="CASCADE"), nullable=False, index=True)
    tecnico_id = Column(Integer, ForeignKey("tecnici.id"), nullable=True)

    azione = Column(String(100), nullable=False)  # CREATO, ASSEGNATO, MODIFICATO, CHIUSO, etc.
    campo_modificato = Column(String(100))
    valore_precedente = Column(Text)
    valore_nuovo = Column(Text)
    descrizione = Column(Text)

    # Relationships
    ticket = relationship("Ticket")
    tecnico = relationship("Tecnico")
