from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Tecnico(BaseModel):
    """Tecnici / Operatori del sistema"""

    __tablename__ = "tecnici"

    # Credenziali
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)

    # Dati anagrafici
    nome = Column(String(100), nullable=False)
    cognome = Column(String(100), nullable=False)

    # Contatti
    telefono = Column(String(50))
    cellulare = Column(String(50))
    interno_telefonico = Column(String(20))
    telegram_id = Column(String(100))

    # Organizzazione
    reparto_id = Column(Integer, ForeignKey("lookup_reparti.id"), nullable=True)
    ruolo_id = Column(Integer, ForeignKey("lookup_ruoli_utente.id"), nullable=False)
    codice_tecnico = Column(String(50), index=True)  # Codice per gestionale

    # LDAP/AD integration
    ldap_dn = Column(String(500))
    ldap_enabled = Column(Integer, default=0)
    username_ad = Column(String(100), index=True)  # Username Active Directory

    # Preferences
    colore_calendario = Column(String(7), default="#3B82F6")
    notifiche_email = Column(Integer, default=1)
    notifiche_push = Column(Integer, default=1)

    # Note
    note = Column(Text)

    # Ultimo accesso
    ultimo_login = Column(DateTime)

    # Relationships
    reparto = relationship("LookupReparti", lazy="joined")
    ruolo = relationship("LookupRuoliUtente", lazy="joined")

    @property
    def nome_completo(self) -> str:
        return f"{self.nome} {self.cognome}"

    @property
    def is_admin(self) -> bool:
        return self.ruolo and self.ruolo.codice == "ADMIN"

    @property
    def is_tecnico(self) -> bool:
        return self.ruolo and self.ruolo.codice in ["ADMIN", "TECNICO"]


class ClientePortale(BaseModel):
    """Utenti cliente per accesso al portale self-service"""

    __tablename__ = "clienti_portale"

    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    nome = Column(String(100), nullable=False)
    cognome = Column(String(100), nullable=False)
    telefono = Column(String(50))

    # Collegamento a cliente gestionale
    cliente_id = Column(Integer, ForeignKey("cache_clienti.id"), nullable=False)

    # Permessi
    visualizza_tutti_ticket_azienda = Column(Integer, default=0)
    puo_aprire_ticket = Column(Integer, default=1)

    # Token reset password
    reset_token = Column(String(255))
    reset_token_expires = Column(DateTime)

    # 2FA (opzionale)
    totp_secret = Column(String(32))
    totp_enabled = Column(Integer, default=0)

    # Ultimo accesso
    ultimo_login = Column(DateTime)

    # Relationships
    cliente = relationship("CacheClienti", lazy="joined")

    @property
    def nome_completo(self) -> str:
        return f"{self.nome} {self.cognome}"
