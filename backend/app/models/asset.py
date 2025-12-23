from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Asset(BaseModel):
    """Inventario asset clienti"""

    __tablename__ = "asset"

    cliente_id = Column(Integer, ForeignKey("cache_clienti.id"), nullable=False, index=True)

    # Tipo asset
    tipo = Column(String(50), nullable=False, index=True)  # SERVER, PC, FIREWALL, SWITCH, etc.

    # Identificazione
    hostname = Column(String(255))
    indirizzo_ip = Column(String(50))
    mac_address = Column(String(17))
    serial_number = Column(String(100))
    asset_tag = Column(String(100))

    # Sistema
    sistema_operativo = Column(String(200))
    versione_os = Column(String(100))

    # Specifiche (JSON)
    specifiche_hardware = Column(Text)  # JSON: CPU, RAM, Dischi, etc.
    licenze_software = Column(Text)  # JSON: array di licenze

    # Stato
    stato = Column(String(50), default="ATTIVO")  # ATTIVO, DISMISSIONE, GUASTO, SOSTITUITO
    ubicazione_fisica = Column(String(255))

    # Contratto/Garanzia
    contratto_id = Column(Integer, ForeignKey("cache_contratti.id"), nullable=True)
    garanzia_scadenza = Column(DateTime)
    fornitore = Column(String(200))

    # Note
    note = Column(Text)

    # Relationships
    cliente = relationship("CacheClienti", lazy="joined")
    contratto = relationship("CacheContratti")

    # One-to-many
    credenziali = relationship("AssetCredenziale", back_populates="asset", lazy="dynamic")
    storico = relationship("AssetStorico", back_populates="asset", lazy="dynamic")


class AssetCredenziale(BaseModel):
    """Credenziali asset (vault criptato)"""

    __tablename__ = "asset_credenziali"

    asset_id = Column(Integer, ForeignKey("asset.id", ondelete="CASCADE"), nullable=False, index=True)

    tipo = Column(String(50))  # SSH, RDP, WEB, DATABASE, etc.
    descrizione = Column(String(200))

    username = Column(String(255))
    password_encrypted = Column(Text)  # AES-256 encrypted
    note_encrypted = Column(Text)  # AES-256 encrypted

    scadenza = Column(DateTime)
    ultima_rotazione = Column(DateTime)

    # Relationships
    asset = relationship("Asset", back_populates="credenziali")

    # Access log
    accessi = relationship("AssetCredenzialeAccesso", back_populates="credenziale", lazy="dynamic")


class AssetCredenzialeAccesso(BaseModel):
    """Log accessi alle credenziali"""

    __tablename__ = "asset_credenziali_accessi"

    credenziale_id = Column(Integer, ForeignKey("asset_credenziali.id", ondelete="CASCADE"), nullable=False, index=True)
    tecnico_id = Column(Integer, ForeignKey("tecnici.id"), nullable=False)

    motivo = Column(String(200))
    ip_address = Column(String(50))

    # Relationships
    credenziale = relationship("AssetCredenziale", back_populates="accessi")
    tecnico = relationship("Tecnico")


class AssetStorico(BaseModel):
    """Storico modifiche asset"""

    __tablename__ = "asset_storico"

    asset_id = Column(Integer, ForeignKey("asset.id", ondelete="CASCADE"), nullable=False, index=True)
    tecnico_id = Column(Integer, ForeignKey("tecnici.id"), nullable=True)
    intervento_id = Column(Integer, ForeignKey("interventi.id"), nullable=True)

    azione = Column(String(100), nullable=False)
    campo_modificato = Column(String(100))
    valore_precedente = Column(Text)
    valore_nuovo = Column(Text)
    descrizione = Column(Text)

    # Relationships
    asset = relationship("Asset", back_populates="storico")
    tecnico = relationship("Tecnico")
    intervento = relationship("Intervento")
