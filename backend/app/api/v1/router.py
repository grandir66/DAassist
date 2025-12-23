from fastapi import APIRouter
from app.api.v1 import auth, lookup, tickets, clients, interventions, dashboard, technicians, contracts, sites, contacts

api_router = APIRouter()

# Include routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(lookup.router, prefix="/lookup", tags=["Lookup Tables"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(tickets.router, prefix="/tickets", tags=["Tickets"])
api_router.include_router(clients.router, prefix="/clients", tags=["Clients"])
api_router.include_router(sites.router, tags=["Sites"])  # No prefix, uses /clients/{id}/sites
api_router.include_router(contacts.router, tags=["Contacts"])  # No prefix, uses /clients/{id}/contacts
api_router.include_router(interventions.router, prefix="/interventions", tags=["Interventions"])
api_router.include_router(technicians.router, prefix="/technicians", tags=["Technicians"])
api_router.include_router(contracts.router, prefix="/contracts", tags=["Contracts"])

# TODO: Add other routers as they are implemented
# api_router.include_router(calendar.router, prefix="/calendar", tags=["Calendar"])
# api_router.include_router(assets.router, prefix="/assets", tags=["Assets"])
# api_router.include_router(kb.router, prefix="/kb", tags=["Knowledge Base"])
# api_router.include_router(sync.router, prefix="/sync", tags=["Sync"])
