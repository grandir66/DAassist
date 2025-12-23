from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import Optional, List
from datetime import datetime

from app.models.ticket import Ticket, TicketNota, TicketMessaggio, TicketStorico
from app.schemas.ticket import TicketCreate, TicketUpdate


class TicketRepository:
    """Repository per operazioni CRUD sui ticket"""

    def __init__(self, db: Session):
        self.db = db

    def get_all(
        self,
        skip: int = 0,
        limit: int = 20,
        stato_id: Optional[int] = None,
        priorita_id: Optional[int] = None,
        tecnico_id: Optional[int] = None,
        cliente_id: Optional[int] = None,
        search: Optional[str] = None,
    ) -> tuple[List[Ticket], int]:
        """Get all tickets with filters"""
        query = self.db.query(Ticket).filter(Ticket.attivo == True)

        # Apply filters
        if stato_id:
            query = query.filter(Ticket.stato_id == stato_id)
        if priorita_id:
            query = query.filter(Ticket.priorita_id == priorita_id)
        if tecnico_id:
            query = query.filter(Ticket.tecnico_assegnato_id == tecnico_id)
        if cliente_id:
            query = query.filter(Ticket.cliente_id == cliente_id)
        if search:
            search_filter = or_(
                Ticket.numero.ilike(f"%{search}%"),
                Ticket.oggetto.ilike(f"%{search}%"),
                Ticket.descrizione.ilike(f"%{search}%"),
            )
            query = query.filter(search_filter)

        # Get total count
        total = query.count()

        # Apply pagination and order
        tickets = query.order_by(Ticket.created_at.desc()).offset(skip).limit(limit).all()

        return tickets, total

    def get_by_id(self, ticket_id: int) -> Optional[Ticket]:
        """Get ticket by ID"""
        return self.db.query(Ticket).filter(
            Ticket.id == ticket_id,
            Ticket.attivo == True
        ).first()

    def get_by_numero(self, numero: str) -> Optional[Ticket]:
        """Get ticket by numero"""
        return self.db.query(Ticket).filter(
            Ticket.numero == numero,
            Ticket.attivo == True
        ).first()

    def create(self, ticket_data: TicketCreate, stato_nuovo_id: int) -> Ticket:
        """Create new ticket"""
        # Generate ticket number
        numero = self._generate_ticket_number()

        ticket = Ticket(
            numero=numero,
            **ticket_data.model_dump(),
            stato_id=stato_nuovo_id,
        )

        self.db.add(ticket)
        self.db.commit()
        self.db.refresh(ticket)

        return ticket

    def update(self, ticket: Ticket, update_data: TicketUpdate) -> Ticket:
        """Update ticket"""
        update_dict = update_data.model_dump(exclude_unset=True)

        for field, value in update_dict.items():
            setattr(ticket, field, value)

        self.db.commit()
        self.db.refresh(ticket)

        return ticket

    def assign(self, ticket: Ticket, tecnico_id: int) -> Ticket:
        """Assign ticket to technician"""
        ticket.tecnico_assegnato_id = tecnico_id

        # Se è la prima assegnazione, registra prima risposta per SLA
        if not ticket.sla_prima_risposta_at:
            ticket.sla_prima_risposta_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(ticket)

        return ticket

    def close(self, ticket: Ticket, tipo_chiusura: str, note_chiusura: str, stato_chiuso_id: int) -> Ticket:
        """Close ticket"""
        ticket.stato_id = stato_chiuso_id
        ticket.tipo_chiusura = tipo_chiusura
        ticket.note_chiusura = note_chiusura
        ticket.data_chiusura = datetime.utcnow()

        self.db.commit()
        self.db.refresh(ticket)

        return ticket

    def add_note(self, ticket_id: int, tecnico_id: int, nota: str) -> TicketNota:
        """Add internal note to ticket"""
        note = TicketNota(
            ticket_id=ticket_id,
            tecnico_id=tecnico_id,
            nota=nota,
        )

        self.db.add(note)
        self.db.commit()
        self.db.refresh(note)

        return note

    def add_messaggio(
        self,
        ticket_id: int,
        mittente_tipo: str,
        messaggio: str,
        mittente_tecnico_id: Optional[int] = None,
        mittente_cliente_id: Optional[int] = None,
    ) -> TicketMessaggio:
        """Add message to ticket"""
        msg = TicketMessaggio(
            ticket_id=ticket_id,
            mittente_tipo=mittente_tipo,
            mittente_tecnico_id=mittente_tecnico_id,
            mittente_cliente_id=mittente_cliente_id,
            messaggio=messaggio,
        )

        self.db.add(msg)
        self.db.commit()
        self.db.refresh(msg)

        return msg

    def log_action(
        self,
        ticket_id: int,
        tecnico_id: Optional[int],
        azione: str,
        descrizione: Optional[str] = None,
        campo_modificato: Optional[str] = None,
        valore_precedente: Optional[str] = None,
        valore_nuovo: Optional[str] = None,
    ) -> TicketStorico:
        """Log ticket action to history"""
        storico = TicketStorico(
            ticket_id=ticket_id,
            tecnico_id=tecnico_id,
            azione=azione,
            descrizione=descrizione,
            campo_modificato=campo_modificato,
            valore_precedente=valore_precedente,
            valore_nuovo=valore_nuovo,
        )

        self.db.add(storico)
        self.db.commit()
        self.db.refresh(storico)

        return storico

    def _generate_ticket_number(self) -> str:
        """Generate unique ticket number"""
        # Get current year
        year = datetime.utcnow().year

        # Get last ticket number for this year
        last_ticket = (
            self.db.query(Ticket)
            .filter(Ticket.numero.like(f"TK-{year}-%"))
            .order_by(Ticket.numero.desc())
            .first()
        )

        if last_ticket:
            # Extract number and increment
            last_num = int(last_ticket.numero.split("-")[-1])
            new_num = last_num + 1
        else:
            new_num = 1

        return f"TK-{year}-{new_num:05d}"

    def soft_delete(self, ticket: Ticket) -> None:
        """Soft delete ticket"""
        ticket.attivo = False
        self.db.commit()
