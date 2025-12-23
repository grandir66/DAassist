from sqlalchemy import Column, String, Integer, DateTime, Text
from app.models.base import BaseModel


class SyncLog(BaseModel):
    """Log delle sincronizzazioni con il gestionale"""

    __tablename__ = "sync_log"

    tipo = Column(String(50), nullable=False, index=True)  # CLIENTI, CONTRATTI, REFERENTI, INTERVENTI
    direzione = Column(String(20), nullable=False)  # IMPORT, EXPORT

    # Risultati
    records_processati = Column(Integer, default=0)
    records_inseriti = Column(Integer, default=0)
    records_aggiornati = Column(Integer, default=0)
    records_errori = Column(Integer, default=0)

    # Durata
    inizio = Column(DateTime, nullable=False)
    fine = Column(DateTime)
    durata_secondi = Column(Integer)

    # Errori
    successo = Column(Integer, default=True)
    errore = Column(Text)
    dettagli_errori = Column(Text)  # JSON array di errori specifici

    # Metadata
    triggered_by = Column(String(50))  # SCHEDULER, MANUAL, API
