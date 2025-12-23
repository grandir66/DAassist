from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.api.v1.auth import get_current_user
from app.models.user import Tecnico
from app.repositories.dashboard import DashboardRepository
from app.schemas.dashboard import (
    DashboardResponse,
    DashboardTicketStats,
    DashboardInterventoStats,
    TicketRecente,
    InterventoOggi,
)

router = APIRouter()


@router.get("", response_model=DashboardResponse)
async def get_dashboard(
    db: Session = Depends(get_db),
    current_user: Tecnico = Depends(get_current_user),
):
    """Get dashboard aggregated statistics"""
    repo = DashboardRepository(db)

    # Get ticket stats
    ticket_stats_data = repo.get_ticket_stats()
    ticket_stats = DashboardTicketStats(**ticket_stats_data)

    # Get intervention stats
    intervento_stats_data = repo.get_intervento_stats()
    intervento_stats = DashboardInterventoStats(**intervento_stats_data)

    # Get recent tickets
    recent_tickets_data = repo.get_recent_tickets(limit=5)
    recent_tickets = [
        TicketRecente(
            id=t.id,
            numero=t.numero,
            cliente_ragione_sociale=t.cliente.ragione_sociale if t.cliente else None,
            oggetto=t.oggetto,
            priorita_codice=t.priorita.codice if t.priorita else "NORMALE",
            priorita_descrizione=t.priorita.descrizione if t.priorita else "Normale",
            stato_codice=t.stato.codice if t.stato else "NUOVO",
            stato_descrizione=t.stato.descrizione if t.stato else "Nuovo",
            created_at=t.created_at,
        )
        for t in recent_tickets_data
    ]

    # Get today's interventions
    interventi_oggi_data = repo.get_interventi_oggi()
    interventi_oggi = [
        InterventoOggi(
            id=i.id,
            numero=i.numero,
            cliente_ragione_sociale=i.cliente.ragione_sociale if i.cliente else "",
            oggetto=i.oggetto,
            tipo_descrizione=i.tipo.descrizione if i.tipo else "",
            tipo_richiede_viaggio=i.tipo.richiede_viaggio if i.tipo else False,
            stato_codice=i.stato.codice if i.stato else "",
            stato_descrizione=i.stato.descrizione if i.stato else "",
            data_inizio=i.data_inizio,
        )
        for i in interventi_oggi_data
    ]

    return DashboardResponse(
        ticket_stats=ticket_stats,
        intervento_stats=intervento_stats,
        recent_tickets=recent_tickets,
        interventi_oggi=interventi_oggi,
    )
