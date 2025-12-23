"""
Script per inizializzare il database con dati di base
"""
from datetime import datetime
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models.base import Base
from app.models.lookup import *
from app.models.user import Tecnico
from app.core.security import get_password_hash


def init_lookup_tables(db: Session):
    """Popola le tabelle di lookup con valori predefiniti"""

    print("Inizializzazione tabelle lookup...")

    # Canali Richiesta
    canali = [
        {"codice": "TELEFONO", "descrizione": "Telefono", "ordine": 1},
        {"codice": "EMAIL", "descrizione": "Email", "ordine": 2},
        {"codice": "WEBAPP", "descrizione": "Web App", "ordine": 3},
        {"codice": "VOCE", "descrizione": "Voce", "ordine": 4},
        {"codice": "PORTALE", "descrizione": "Portale Cliente", "ordine": 5},
        {"codice": "MONITORING", "descrizione": "Sistema Monitoring", "ordine": 6},
    ]
    for c in canali:
        if not db.query(LookupCanaliRichiesta).filter_by(codice=c["codice"]).first():
            db.add(LookupCanaliRichiesta(**c))

    # Priorità
    priorita = [
        {"codice": "CRITICA", "descrizione": "Critica", "livello": 1, "colore": "#DC2626", "ordine": 1},
        {"codice": "URGENTE", "descrizione": "Urgente", "livello": 2, "colore": "#EA580C", "ordine": 2},
        {"codice": "ALTA", "descrizione": "Alta", "livello": 3, "colore": "#F59E0B", "ordine": 3},
        {"codice": "NORMALE", "descrizione": "Normale", "livello": 4, "colore": "#3B82F6", "ordine": 4},
        {"codice": "BASSA", "descrizione": "Bassa", "livello": 5, "colore": "#6B7280", "ordine": 5},
    ]
    for p in priorita:
        if not db.query(LookupPriorita).filter_by(codice=p["codice"]).first():
            db.add(LookupPriorita(**p))

    # Stati Ticket
    stati_ticket = [
        {"codice": "NUOVO", "descrizione": "Nuovo", "colore": "#3B82F6", "ordine": 1, "finale": False},
        {"codice": "PRESO_CARICO", "descrizione": "Preso in carico", "colore": "#8B5CF6", "ordine": 2, "finale": False},
        {"codice": "IN_LAVORAZIONE", "descrizione": "In lavorazione", "colore": "#F59E0B", "ordine": 3, "finale": False},
        {"codice": "SCHEDULATO", "descrizione": "Schedulato", "colore": "#06B6D4", "ordine": 4, "finale": False},
        {"codice": "CHIUSO", "descrizione": "Chiuso", "colore": "#10B981", "ordine": 5, "finale": True},
        {"codice": "ANNULLATO", "descrizione": "Annullato", "colore": "#EF4444", "ordine": 6, "finale": True},
    ]
    for s in stati_ticket:
        if not db.query(LookupStatiTicket).filter_by(codice=s["codice"]).first():
            db.add(LookupStatiTicket(**s))

    # Stati Intervento
    stati_intervento = [
        {"codice": "BOZZA", "descrizione": "Bozza", "colore": "#6B7280", "ordine": 1, "finale": False},
        {"codice": "PIANIFICATO", "descrizione": "Pianificato", "colore": "#3B82F6", "ordine": 2, "finale": False},
        {"codice": "IN_CORSO", "descrizione": "In corso", "colore": "#F59E0B", "ordine": 3, "finale": False},
        {"codice": "COMPLETATO", "descrizione": "Completato", "colore": "#8B5CF6", "ordine": 4, "finale": False},
        {"codice": "CHIUSO", "descrizione": "Chiuso", "colore": "#10B981", "ordine": 5, "finale": True},
        {"codice": "SINCRONIZZATO", "descrizione": "Sincronizzato", "colore": "#059669", "ordine": 6, "finale": True},
    ]
    for s in stati_intervento:
        if not db.query(LookupStatiIntervento).filter_by(codice=s["codice"]).first():
            db.add(LookupStatiIntervento(**s))

    # Tipi Intervento
    tipi_intervento = [
        {"codice": "CLIENTE", "descrizione": "Presso cliente", "colore": "#3B82F6", "richiede_viaggio": True, "ordine": 1},
        {"codice": "LABORATORIO", "descrizione": "In laboratorio", "colore": "#10B981", "richiede_viaggio": False, "ordine": 2},
        {"codice": "REMOTO", "descrizione": "Remoto", "colore": "#F59E0B", "richiede_viaggio": False, "ordine": 3},
        {"codice": "TELEFONICO", "descrizione": "Telefonico", "colore": "#8B5CF6", "richiede_viaggio": False, "ordine": 4},
    ]
    for t in tipi_intervento:
        if not db.query(LookupTipiIntervento).filter_by(codice=t["codice"]).first():
            db.add(LookupTipiIntervento(**t))

    # Categorie Attività
    categorie = [
        {"codice": "TECNICA", "descrizione": "Assistenza Tecnica", "prezzo_unitario_default": 50.00, "ordine": 1},
        {"codice": "SISTEMISTICA", "descrizione": "Sistemistica", "prezzo_unitario_default": 60.00, "ordine": 2},
        {"codice": "GESTIONALE", "descrizione": "Software Gestionale", "prezzo_unitario_default": 55.00, "ordine": 3},
        {"codice": "CENTRALINO", "descrizione": "Centralino VoIP", "prezzo_unitario_default": 50.00, "ordine": 4},
        {"codice": "SECURITY", "descrizione": "Sicurezza Informatica", "prezzo_unitario_default": 70.00, "ordine": 5},
        {"codice": "CONSULENZA", "descrizione": "Consulenza", "prezzo_unitario_default": 80.00, "ordine": 6},
        {"codice": "SVILUPPO", "descrizione": "Sviluppo Software", "prezzo_unitario_default": 75.00, "ordine": 7},
        {"codice": "FORMAZIONE", "descrizione": "Formazione", "prezzo_unitario_default": 60.00, "ordine": 8},
        {"codice": "ALTRO", "descrizione": "Altro", "prezzo_unitario_default": 50.00, "ordine": 9},
    ]
    for c in categorie:
        if not db.query(LookupCategorieAttivita).filter_by(codice=c["codice"]).first():
            db.add(LookupCategorieAttivita(**c))

    # Origini Intervento
    origini = [
        {"codice": "DA_TICKET", "descrizione": "Da Ticket", "ordine": 1},
        {"codice": "DA_PIANIFICAZIONE", "descrizione": "Da Pianificazione", "ordine": 2},
        {"codice": "DA_PROGETTO", "descrizione": "Da Progetto", "ordine": 3},
        {"codice": "SPONTANEO", "descrizione": "Spontaneo", "ordine": 4},
        {"codice": "DA_CONTRATTO", "descrizione": "Da Contratto", "ordine": 5},
    ]
    for o in origini:
        if not db.query(LookupOriginiIntervento).filter_by(codice=o["codice"]).first():
            db.add(LookupOriginiIntervento(**o))

    # Reparti
    reparti = [
        {"codice": "TECNICO", "descrizione": "Reparto Tecnico", "email": "tecnico@daassist.local", "ordine": 1},
        {"codice": "SISTEMISTICA", "descrizione": "Sistemistica", "email": "sistemistica@daassist.local", "ordine": 2},
        {"codice": "SVILUPPO", "descrizione": "Sviluppo", "email": "sviluppo@daassist.local", "ordine": 3},
        {"codice": "AMMINISTRAZIONE", "descrizione": "Amministrazione", "email": "admin@daassist.local", "ordine": 4},
    ]
    for r in reparti:
        if not db.query(LookupReparti).filter_by(codice=r["codice"]).first():
            db.add(LookupReparti(**r))

    # Ruoli Utente
    ruoli = [
        {"codice": "ADMIN", "descrizione": "Amministratore", "permessi": '["*"]', "ordine": 1},
        {"codice": "TECNICO", "descrizione": "Tecnico", "permessi": '["tickets.*", "interventions.*"]', "ordine": 2},
        {"codice": "OPERATORE", "descrizione": "Operatore", "permessi": '["tickets.read", "tickets.create"]', "ordine": 3},
        {"codice": "CLIENTE", "descrizione": "Cliente", "permessi": '["tickets.read", "tickets.create"]', "ordine": 4},
    ]
    for r in ruoli:
        if not db.query(LookupRuoliUtente).filter_by(codice=r["codice"]).first():
            db.add(LookupRuoliUtente(**r))

    db.commit()
    print("✓ Tabelle lookup inizializzate")


def create_admin_user(db: Session):
    """Crea utente amministratore di default"""

    print("Creazione utente amministratore...")

    admin_role = db.query(LookupRuoliUtente).filter_by(codice="ADMIN").first()
    if not admin_role:
        print("✗ Ruolo ADMIN non trovato!")
        return

    # Verifica se admin esiste già
    existing_admin = db.query(Tecnico).filter_by(username="admin").first()
    if existing_admin:
        print("✓ Utente admin già esistente")
        return

    admin = Tecnico(
        username="admin",
        email="admin@daassist.local",
        hashed_password=get_password_hash("admin123"),  # Password di default - CAMBIARE IN PRODUZIONE!
        nome="Admin",
        cognome="DAAssist",
        ruolo_id=admin_role.id,
        ldap_enabled=0,
        colore_calendario="#DC2626",
    )
    db.add(admin)
    db.commit()

    print("✓ Utente admin creato (username: admin, password: admin123)")
    print("⚠️  IMPORTANTE: Cambiare la password admin in produzione!")


def main():
    """Main function"""
    print("\n" + "="*60)
    print("Inizializzazione Database DAAssist")
    print("="*60 + "\n")

    # Crea tutte le tabelle
    print("Creazione tabelle database...")
    Base.metadata.create_all(bind=engine)
    print("✓ Tabelle create\n")

    # Popola lookup tables
    db = SessionLocal()
    try:
        init_lookup_tables(db)
        print()
        create_admin_user(db)
        print()
        print("="*60)
        print("Inizializzazione completata con successo!")
        print("="*60)
        print("\nIl backend è pronto per essere avviato.")
        print("Accedi con: username=admin, password=admin123\n")
    except Exception as e:
        print(f"\n✗ Errore durante l'inizializzazione: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
