from app.models.base import Base, BaseModel
from app.models.lookup import (
    LookupCanaliRichiesta,
    LookupPriorita,
    LookupStatiTicket,
    LookupStatiIntervento,
    LookupTipiIntervento,
    LookupCategorieAttivita,
    LookupOriginiIntervento,
    LookupReparti,
    LookupRuoliUtente,
)
from app.models.user import Tecnico, ClientePortale
from app.models.client import CacheClienti, CacheContratti, CacheReferenti, SLADefinizione
from app.models.ticket import (
    Ticket,
    TicketNota,
    TicketMessaggio,
    TicketAllegato,
    TicketStorico,
)
from app.models.intervention import (
    Intervento,
    InterventoRiga,
    InterventoSessione,
    InterventoTecnico,
    InterventoAllegato,
    RichiestaIntervento,
)
from app.models.calendar import (
    CalendarioEvento,
    CalendarioTecnico,
    CalendarioSyncLog,
)
from app.models.asset import (
    Asset,
    AssetCredenziale,
    AssetCredenzialeAccesso,
    AssetStorico,
)
from app.models.kb import (
    KBCategoria,
    KBArticolo,
    KBTag,
    KBArticoloTag,
    KBArticoloFeedback,
)
from app.models.sync import SyncLog

__all__ = [
    "Base",
    "BaseModel",
    # Lookup
    "LookupCanaliRichiesta",
    "LookupPriorita",
    "LookupStatiTicket",
    "LookupStatiIntervento",
    "LookupTipiIntervento",
    "LookupCategorieAttivita",
    "LookupOriginiIntervento",
    "LookupReparti",
    "LookupRuoliUtente",
    # Users
    "Tecnico",
    "ClientePortale",
    # Clients
    "CacheClienti",
    "CacheContratti",
    "CacheReferenti",
    "SLADefinizione",
    # Tickets
    "Ticket",
    "TicketNota",
    "TicketMessaggio",
    "TicketAllegato",
    "TicketStorico",
    # Interventions
    "Intervento",
    "InterventoRiga",
    "InterventoSessione",
    "InterventoTecnico",
    "InterventoAllegato",
    "RichiestaIntervento",
    # Calendar
    "CalendarioEvento",
    "CalendarioTecnico",
    "CalendarioSyncLog",
    # Assets
    "Asset",
    "AssetCredenziale",
    "AssetCredenzialeAccesso",
    "AssetStorico",
    # KB
    "KBCategoria",
    "KBArticolo",
    "KBTag",
    "KBArticoloTag",
    "KBArticoloFeedback",
    # Sync
    "SyncLog",
]
