from typing import List, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, and_, or_

from app.models.ticket import Ticket
from app.models.intervention import Intervento
from app.models.lookup import LookupStatiTicket, LookupStatiIntervento


class DashboardRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_ticket_stats(self) -> dict:
        """Get aggregated ticket statistics"""
        now = datetime.utcnow()
        today_start = datetime(now.year, now.month, now.day, 0, 0, 0)
        week_start = today_start - timedelta(days=today_start.weekday())
        month_start = datetime(now.year, now.month, 1, 0, 0, 0)

        # Total active tickets
        totali = self.db.query(Ticket).filter(Ticket.attivo == True).count()

        # Open tickets (not in final states)
        aperti = (
            self.db.query(Ticket)
            .join(LookupStatiTicket)
            .filter(Ticket.attivo == True, LookupStatiTicket.finale == 0)
            .count()
        )

        # New tickets
        nuovi = (
            self.db.query(Ticket)
            .join(LookupStatiTicket)
            .filter(Ticket.attivo == True, LookupStatiTicket.codice == "NUOVO")
            .count()
        )

        # In progress (PRESO_CARICO or IN_LAVORAZIONE)
        in_lavorazione = (
            self.db.query(Ticket)
            .join(LookupStatiTicket)
            .filter(
                Ticket.attivo == True,
                or_(
                    LookupStatiTicket.codice == "PRESO_CARICO",
                    LookupStatiTicket.codice == "IN_LAVORAZIONE",
                ),
            )
            .count()
        )

        # Closed today
        chiusi_oggi = (
            self.db.query(Ticket)
            .filter(
                Ticket.attivo == True,
                Ticket.data_chiusura >= today_start,
                Ticket.data_chiusura < today_start + timedelta(days=1),
            )
            .count()
        )

        # Closed this week
        chiusi_settimana = (
            self.db.query(Ticket)
            .filter(
                Ticket.attivo == True,
                Ticket.data_chiusura >= week_start,
                Ticket.data_chiusura < today_start + timedelta(days=1),
            )
            .count()
        )

        # Closed this month
        chiusi_mese = (
            self.db.query(Ticket)
            .filter(
                Ticket.attivo == True,
                Ticket.data_chiusura >= month_start,
                Ticket.data_chiusura < today_start + timedelta(days=1),
            )
            .count()
        )

        return {
            "totali": totali,
            "aperti": aperti,
            "nuovi": nuovi,
            "in_lavorazione": in_lavorazione,
            "chiusi_oggi": chiusi_oggi,
            "chiusi_settimana": chiusi_settimana,
            "chiusi_mese": chiusi_mese,
        }

    def get_intervento_stats(self) -> dict:
        """Get aggregated intervention statistics"""
        now = datetime.utcnow()
        today_start = datetime(now.year, now.month, now.day, 0, 0, 0)
        week_start = today_start - timedelta(days=today_start.weekday())
        month_start = datetime(now.year, now.month, 1, 0, 0, 0)

        # Total active interventions
        totali = self.db.query(Intervento).filter(Intervento.attivo == True).count()

        # Planned interventions
        pianificati = (
            self.db.query(Intervento)
            .join(LookupStatiIntervento)
            .filter(
                Intervento.attivo == True, LookupStatiIntervento.codice == "PIANIFICATO"
            )
            .count()
        )

        # In progress
        in_corso = (
            self.db.query(Intervento)
            .join(LookupStatiIntervento)
            .filter(Intervento.attivo == True, LookupStatiIntervento.codice == "IN_CORSO")
            .count()
        )

        # Completed today
        completati_oggi = (
            self.db.query(Intervento)
            .filter(
                Intervento.attivo == True,
                Intervento.data_fine >= today_start,
                Intervento.data_fine < today_start + timedelta(days=1),
            )
            .count()
        )

        # Completed this week
        completati_settimana = (
            self.db.query(Intervento)
            .filter(
                Intervento.attivo == True,
                Intervento.data_fine >= week_start,
                Intervento.data_fine < today_start + timedelta(days=1),
            )
            .count()
        )

        # Completed this month
        completati_mese = (
            self.db.query(Intervento)
            .filter(
                Intervento.attivo == True,
                Intervento.data_fine >= month_start,
                Intervento.data_fine < today_start + timedelta(days=1),
            )
            .count()
        )

        return {
            "totali": totali,
            "pianificati": pianificati,
            "in_corso": in_corso,
            "completati_oggi": completati_oggi,
            "completati_settimana": completati_settimana,
            "completati_mese": completati_mese,
        }

    def get_recent_tickets(self, limit: int = 5) -> List[Ticket]:
        """Get recent tickets"""
        return (
            self.db.query(Ticket)
            .options(
                joinedload(Ticket.cliente),
                joinedload(Ticket.priorita),
                joinedload(Ticket.stato),
            )
            .filter(Ticket.attivo == True)
            .order_by(Ticket.created_at.desc())
            .limit(limit)
            .all()
        )

    def get_interventi_oggi(self) -> List[Intervento]:
        """Get interventions scheduled for today"""
        now = datetime.utcnow()
        today_start = datetime(now.year, now.month, now.day, 0, 0, 0)
        today_end = today_start + timedelta(days=1)

        return (
            self.db.query(Intervento)
            .options(
                joinedload(Intervento.cliente),
                joinedload(Intervento.tipo),
                joinedload(Intervento.stato),
            )
            .filter(
                Intervento.attivo == True,
                Intervento.data_inizio >= today_start,
                Intervento.data_inizio < today_end,
            )
            .order_by(Intervento.data_inizio.asc())
            .all()
        )
