from typing import List, Optional, Tuple
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, func

from app.models.client import CacheClienti, CacheContratti, CacheReferenti


class ClientRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(
        self,
        skip: int = 0,
        limit: int = 20,
        search: Optional[str] = None,
        attivo: Optional[bool] = None,
    ) -> Tuple[List[CacheClienti], int]:
        """Get all clients with optional filters"""
        query = self.db.query(CacheClienti)

        # Apply filters
        if attivo is not None:
            query = query.filter(CacheClienti.attivo == attivo)

        if search:
            search_filter = f"%{search}%"
            query = query.filter(
                or_(
                    CacheClienti.ragione_sociale.ilike(search_filter),
                    CacheClienti.codice_gestionale.ilike(search_filter),
                    CacheClienti.partita_iva.ilike(search_filter),
                    CacheClienti.email.ilike(search_filter),
                )
            )

        # Get total count
        total = query.count()

        # Apply pagination
        clienti = query.order_by(CacheClienti.ragione_sociale).offset(skip).limit(limit).all()

        return clienti, total

    def get_by_id(self, cliente_id: int) -> Optional[CacheClienti]:
        """Get client by ID"""
        return (
            self.db.query(CacheClienti)
            .filter(CacheClienti.id == cliente_id, CacheClienti.attivo == True)
            .first()
        )

    def get_by_codice(self, codice_gestionale: str) -> Optional[CacheClienti]:
        """Get client by codice gestionale"""
        return (
            self.db.query(CacheClienti)
            .filter(
                CacheClienti.codice_gestionale == codice_gestionale,
                CacheClienti.attivo == True,
            )
            .first()
        )

    def get_contratti(self, cliente_id: int) -> List[CacheContratti]:
        """Get all contracts for a client"""
        return (
            self.db.query(CacheContratti)
            .filter(
                CacheContratti.cliente_id == cliente_id,
                CacheContratti.attivo == True,
            )
            .order_by(CacheContratti.data_inizio.desc())
            .all()
        )

    def get_referenti(self, cliente_id: int) -> List[CacheReferenti]:
        """Get all contacts for a client"""
        return (
            self.db.query(CacheReferenti)
            .filter(
                CacheReferenti.cliente_id == cliente_id,
                CacheReferenti.attivo == True,
            )
            .order_by(CacheReferenti.contatto_principale.desc(), CacheReferenti.cognome)
            .all()
        )

    def get_stats(self, cliente_id: int) -> dict:
        """Get statistics for a client"""
        from app.models.ticket import Ticket
        from app.models.intervention import Intervento

        # Count tickets
        total_tickets = (
            self.db.query(func.count(Ticket.id))
            .filter(Ticket.cliente_id == cliente_id, Ticket.attivo == True)
            .scalar()
        )

        open_tickets = (
            self.db.query(func.count(Ticket.id))
            .join(Ticket.stato)
            .filter(
                Ticket.cliente_id == cliente_id,
                Ticket.attivo == True,
                Ticket.stato.has(finale=0),
            )
            .scalar()
        )

        # Count interventions
        total_interventi = (
            self.db.query(func.count(Intervento.id))
            .filter(Intervento.cliente_id == cliente_id, Intervento.attivo == True)
            .scalar()
        )

        return {
            "total_tickets": total_tickets or 0,
            "open_tickets": open_tickets or 0,
            "total_interventi": total_interventi or 0,
        }
