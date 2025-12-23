from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.api.v1.auth import get_current_user
from app.models.user import Tecnico
from app.models.lookup import LookupStatiTicket
from app.repositories.ticket import TicketRepository
from app.schemas.ticket import (
    TicketCreate,
    TicketUpdate,
    TicketResponse,
    TicketListResponse,
    TicketAssignRequest,
    TicketCloseRequest,
    TicketNoteCreate,
    TicketMessaggioCreate,
)

router = APIRouter()


@router.get("", response_model=TicketListResponse)
async def get_tickets(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    stato_id: Optional[int] = None,
    priorita_id: Optional[int] = None,
    tecnico_id: Optional[int] = None,
    cliente_id: Optional[int] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Tecnico = Depends(get_current_user),
):
    """Get list of tickets with filters and pagination"""
    repo = TicketRepository(db)

    skip = (page - 1) * limit
    tickets, total = repo.get_all(
        skip=skip,
        limit=limit,
        stato_id=stato_id,
        priorita_id=priorita_id,
        tecnico_id=tecnico_id,
        cliente_id=cliente_id,
        search=search,
    )

    return TicketListResponse(
        total=total,
        page=page,
        limit=limit,
        tickets=tickets,
    )


@router.post("", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
async def create_ticket(
    ticket_data: TicketCreate,
    db: Session = Depends(get_db),
    current_user: Tecnico = Depends(get_current_user),
):
    """Create new ticket"""
    repo = TicketRepository(db)

    # Get NUOVO state
    stato_nuovo = db.query(LookupStatiTicket).filter_by(codice="NUOVO", attivo=True).first()
    if not stato_nuovo:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Stato NUOVO non trovato",
        )

    ticket = repo.create(ticket_data, stato_nuovo.id)

    # Log creation
    repo.log_action(
        ticket_id=ticket.id,
        tecnico_id=current_user.id,
        azione="CREATO",
        descrizione=f"Ticket creato da {current_user.nome_completo}",
    )

    return ticket


@router.get("/{ticket_id}", response_model=TicketResponse)
async def get_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: Tecnico = Depends(get_current_user),
):
    """Get ticket by ID"""
    repo = TicketRepository(db)
    ticket = repo.get_by_id(ticket_id)

    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket {ticket_id} non trovato",
        )

    return ticket


@router.patch("/{ticket_id}", response_model=TicketResponse)
async def update_ticket(
    ticket_id: int,
    update_data: TicketUpdate,
    db: Session = Depends(get_db),
    current_user: Tecnico = Depends(get_current_user),
):
    """Update ticket"""
    repo = TicketRepository(db)
    ticket = repo.get_by_id(ticket_id)

    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket {ticket_id} non trovato",
        )

    ticket = repo.update(ticket, update_data)

    # Log update
    repo.log_action(
        ticket_id=ticket.id,
        tecnico_id=current_user.id,
        azione="MODIFICATO",
        descrizione=f"Ticket modificato da {current_user.nome_completo}",
    )

    return ticket


@router.post("/{ticket_id}/assign", response_model=TicketResponse)
async def assign_ticket(
    ticket_id: int,
    assign_data: TicketAssignRequest,
    db: Session = Depends(get_db),
    current_user: Tecnico = Depends(get_current_user),
):
    """Assign ticket to technician"""
    repo = TicketRepository(db)
    ticket = repo.get_by_id(ticket_id)

    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket {ticket_id} non trovato",
        )

    # Check if technician exists
    tecnico = db.query(Tecnico).filter_by(id=assign_data.tecnico_id, attivo=True).first()
    if not tecnico:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tecnico {assign_data.tecnico_id} non trovato",
        )

    ticket = repo.assign(ticket, assign_data.tecnico_id)

    # Log assignment
    repo.log_action(
        ticket_id=ticket.id,
        tecnico_id=current_user.id,
        azione="ASSEGNATO",
        descrizione=f"Ticket assegnato a {tecnico.nome_completo}",
    )

    return ticket


@router.post("/{ticket_id}/take", response_model=TicketResponse)
async def take_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: Tecnico = Depends(get_current_user),
):
    """Take ticket (assign to current user)"""
    repo = TicketRepository(db)
    ticket = repo.get_by_id(ticket_id)

    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket {ticket_id} non trovato",
        )

    ticket = repo.assign(ticket, current_user.id)

    # Update stato to PRESO_CARICO if currently NUOVO
    stato_preso = db.query(LookupStatiTicket).filter_by(codice="PRESO_CARICO", attivo=True).first()
    if stato_preso and ticket.stato.codice == "NUOVO":
        ticket.stato_id = stato_preso.id
        db.commit()
        db.refresh(ticket)

    # Log action
    repo.log_action(
        ticket_id=ticket.id,
        tecnico_id=current_user.id,
        azione="PRESO_CARICO",
        descrizione=f"Ticket preso in carico da {current_user.nome_completo}",
    )

    return ticket


@router.post("/{ticket_id}/close", response_model=TicketResponse)
async def close_ticket(
    ticket_id: int,
    close_data: TicketCloseRequest,
    db: Session = Depends(get_db),
    current_user: Tecnico = Depends(get_current_user),
):
    """Close ticket"""
    repo = TicketRepository(db)
    ticket = repo.get_by_id(ticket_id)

    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket {ticket_id} non trovato",
        )

    # Get CHIUSO state
    stato_chiuso = db.query(LookupStatiTicket).filter_by(codice="CHIUSO", attivo=True).first()
    if not stato_chiuso:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Stato CHIUSO non trovato",
        )

    ticket = repo.close(
        ticket,
        tipo_chiusura=close_data.tipo_chiusura,
        note_chiusura=close_data.note_chiusura,
        stato_chiuso_id=stato_chiuso.id,
    )

    # Log closure
    repo.log_action(
        ticket_id=ticket.id,
        tecnico_id=current_user.id,
        azione="CHIUSO",
        descrizione=f"Ticket chiuso da {current_user.nome_completo} - {close_data.tipo_chiusura}",
    )

    return ticket


@router.post("/{ticket_id}/notes")
async def add_note(
    ticket_id: int,
    note_data: TicketNoteCreate,
    db: Session = Depends(get_db),
    current_user: Tecnico = Depends(get_current_user),
):
    """Add internal note to ticket"""
    repo = TicketRepository(db)
    ticket = repo.get_by_id(ticket_id)

    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket {ticket_id} non trovato",
        )

    note = repo.add_note(ticket_id, current_user.id, note_data.nota)

    return {"id": note.id, "nota": note.nota, "created_at": note.created_at}


@router.post("/{ticket_id}/messages")
async def add_message(
    ticket_id: int,
    message_data: TicketMessaggioCreate,
    db: Session = Depends(get_db),
    current_user: Tecnico = Depends(get_current_user),
):
    """Add message to ticket (visible to client)"""
    repo = TicketRepository(db)
    ticket = repo.get_by_id(ticket_id)

    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket {ticket_id} non trovato",
        )

    messaggio = repo.add_messaggio(
        ticket_id=ticket_id,
        mittente_tipo="TECNICO",
        messaggio=message_data.messaggio,
        mittente_tecnico_id=current_user.id,
    )

    return {
        "id": messaggio.id,
        "messaggio": messaggio.messaggio,
        "mittente_tipo": messaggio.mittente_tipo,
        "created_at": messaggio.created_at,
    }


@router.delete("/{ticket_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: Tecnico = Depends(get_current_user),
):
    """Soft delete ticket (set attivo=False)"""
    repo = TicketRepository(db)
    ticket = repo.get_by_id(ticket_id)

    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket {ticket_id} non trovato",
        )

    # Check if user is admin
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo gli admin possono eliminare ticket",
        )

    repo.soft_delete(ticket)

    # Log deletion
    repo.log_action(
        ticket_id=ticket.id,
        tecnico_id=current_user.id,
        azione="ELIMINATO",
        descrizione=f"Ticket eliminato da {current_user.nome_completo}",
    )

    return None


@router.post("/{ticket_id}/create-intervention", response_model=dict)
async def create_intervention_from_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: Tecnico = Depends(get_current_user),
):
    """Create immediate intervention from ticket and close ticket"""
    from app.models.intervention import Intervento
    from app.models.lookup import LookupStatiIntervento, LookupOriginiIntervento, LookupTipiIntervento
    from datetime import datetime

    repo = TicketRepository(db)
    ticket = repo.get_by_id(ticket_id)

    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket {ticket_id} non trovato",
        )

    # Get required lookups
    stato_in_corso = db.query(LookupStatiIntervento).filter_by(codice="IN_CORSO", attivo=True).first()
    if not stato_in_corso:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Stato IN_CORSO per intervento non trovato",
        )

    origine_ticket = db.query(LookupOriginiIntervento).filter_by(codice="DA_TICKET", attivo=True).first()
    if not origine_ticket:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Origine DA_TICKET non trovata",
        )

    tipo_cliente = db.query(LookupTipiIntervento).filter_by(codice="PRESSO_CLIENTE", attivo=True).first()
    if not tipo_cliente:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Tipo intervento PRESSO_CLIENTE non trovato",
        )

    # Generate intervention number
    current_year = datetime.now().year
    last_intervento = (
        db.query(Intervento)
        .filter(Intervento.numero.like(f"INT-{current_year}-%"))
        .order_by(Intervento.numero.desc())
        .first()
    )
    if last_intervento:
        last_num = int(last_intervento.numero.split("-")[-1])
        new_num = last_num + 1
    else:
        new_num = 1
    numero_intervento = f"INT-{current_year}-{new_num:05d}"

    # Create intervention
    intervento = Intervento(
        numero=numero_intervento,
        ticket_id=ticket.id,
        cliente_id=ticket.cliente_id,
        contratto_id=ticket.contratto_id,
        tecnico_id=current_user.id,
        stato_id=stato_in_corso.id,
        origine_id=origine_ticket.id,
        tipo_intervento_id=tipo_cliente.id,
        oggetto=ticket.oggetto,
        descrizione_lavoro=f"Intervento da ticket #{ticket.numero}\n\n{ticket.descrizione or ''}",
        data_inizio=datetime.now(),
        sincronizzato_gestionale=0,
        attivo=True,
    )
    db.add(intervento)
    db.commit()
    db.refresh(intervento)

    # Update ticket stato to SCHEDULATO
    stato_schedulato = db.query(LookupStatiTicket).filter_by(codice="SCHEDULATO", attivo=True).first()
    if stato_schedulato:
        ticket.stato_id = stato_schedulato.id
        db.commit()

    # Log action
    repo.log_action(
        ticket_id=ticket.id,
        tecnico_id=current_user.id,
        azione="INTERVENTO_CREATO",
        descrizione=f"Creato intervento immediato #{intervento.id}",
    )

    return {
        "intervento_id": intervento.id,
        "ticket_id": ticket.id,
        "message": "Intervento creato con successo"
    }


@router.post("/{ticket_id}/schedule-intervention", response_model=dict)
async def schedule_intervention_from_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: Tecnico = Depends(get_current_user),
):
    """Create scheduled intervention request from ticket"""
    from app.models.intervention import RichiestaIntervento
    from datetime import datetime

    repo = TicketRepository(db)
    ticket = repo.get_by_id(ticket_id)

    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket {ticket_id} non trovato",
        )

    # Create intervention request
    richiesta = RichiestaIntervento(
        ticket_id=ticket.id,
        cliente_id=ticket.cliente_id,
        oggetto=ticket.oggetto,
        descrizione=f"Richiesta da ticket #{ticket.numero}\n\n{ticket.descrizione or ''}",
        priorita_id=ticket.priorita_id if ticket.priorita_id else 3,
        tecnico_richiesto_id=current_user.id,
        stato="PENDENTE",
        data_richiesta=datetime.now(),
        attivo=True,
    )
    db.add(richiesta)
    db.commit()
    db.refresh(richiesta)

    # Update ticket stato to SCHEDULATO
    stato_schedulato = db.query(LookupStatiTicket).filter_by(codice="SCHEDULATO", attivo=True).first()
    if stato_schedulato:
        ticket.stato_id = stato_schedulato.id
        db.commit()

    # Log action
    repo.log_action(
        ticket_id=ticket.id,
        tecnico_id=current_user.id,
        azione="RICHIESTA_INTERVENTO",
        descrizione=f"Creata richiesta intervento pianificato #{richiesta.id}",
    )

    return {
        "richiesta_id": richiesta.id,
        "ticket_id": ticket.id,
        "message": "Richiesta intervento creata con successo"
    }
