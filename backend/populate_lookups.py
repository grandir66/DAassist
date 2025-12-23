"""
Script per popolare le tabelle lookup con dati iniziali
"""
from app.database import SessionLocal
from app.models import *
from datetime import datetime

def populate_lookups():
    db = SessionLocal()

    try:
        print("Popolamento tabelle lookup...")

        # 1. Lookup Canali Richiesta
        print("  - Canali Richiesta")
        canali = [
            {"codice": "EMAIL", "descrizione": "Email", "ordine": 1},
            {"codice": "TELEFONO", "descrizione": "Telefono", "ordine": 2},
            {"codice": "PORTALE", "descrizione": "Portale Web", "ordine": 3},
            {"codice": "WHATSAPP", "descrizione": "WhatsApp", "ordine": 4},
            {"codice": "CHAT", "descrizione": "Chat Live", "ordine": 5},
            {"codice": "DIRETTO", "descrizione": "Contatto Diretto", "ordine": 6},
        ]
        for c in canali:
            exists = db.query(LookupCanaliRichiesta).filter_by(codice=c["codice"]).first()
            if not exists:
                db.add(LookupCanaliRichiesta(**c, attivo=True, created_at=datetime.utcnow(), updated_at=datetime.utcnow()))

        # 2. Lookup Priorità
        print("  - Priorità")
        priorita = [
            {"codice": "CRITICA", "descrizione": "Critica", "livello": 5, "colore": "#DC2626", "ordine": 1},
            {"codice": "URGENTE", "descrizione": "Urgente", "livello": 4, "colore": "#EA580C", "ordine": 2},
            {"codice": "ALTA", "descrizione": "Alta", "livello": 3, "colore": "#F59E0B", "ordine": 3},
            {"codice": "NORMALE", "descrizione": "Normale", "livello": 2, "colore": "#3B82F6", "ordine": 4},
            {"codice": "BASSA", "descrizione": "Bassa", "livello": 1, "colore": "#6B7280", "ordine": 5},
        ]
        for p in priorita:
            exists = db.query(LookupPriorita).filter_by(codice=p["codice"]).first()
            if not exists:
                db.add(LookupPriorita(**p, attivo=True, created_at=datetime.utcnow(), updated_at=datetime.utcnow()))

        # 3. Lookup Stati Ticket
        print("  - Stati Ticket")
        stati_ticket = [
            {"codice": "NUOVO", "descrizione": "Nuovo", "colore": "#3B82F6", "finale": False, "ordine": 1},
            {"codice": "PRESO_CARICO", "descrizione": "Preso in Carico", "colore": "#8B5CF6", "finale": False, "ordine": 2},
            {"codice": "IN_LAVORAZIONE", "descrizione": "In Lavorazione", "colore": "#F59E0B", "finale": False, "ordine": 3},
            {"codice": "ATTESA_CLIENTE", "descrizione": "Attesa Cliente", "colore": "#F59E0B", "finale": False, "ordine": 4},
            {"codice": "SCHEDULATO", "descrizione": "Schedulato", "colore": "#06B6D4", "finale": False, "ordine": 5},
            {"codice": "CHIUSO", "descrizione": "Chiuso", "colore": "#10B981", "finale": True, "ordine": 6},
            {"codice": "ANNULLATO", "descrizione": "Annullato", "colore": "#EF4444", "finale": True, "ordine": 7},
        ]
        for s in stati_ticket:
            exists = db.query(LookupStatiTicket).filter_by(codice=s["codice"]).first()
            if not exists:
                db.add(LookupStatiTicket(**s, attivo=True, created_at=datetime.utcnow(), updated_at=datetime.utcnow()))

        # 4. Lookup Stati Intervento
        print("  - Stati Intervento")
        stati_intervento = [
            {"codice": "PIANIFICATO", "descrizione": "Pianificato", "colore": "#3B82F6", "finale": False, "ordine": 1},
            {"codice": "IN_CORSO", "descrizione": "In Corso", "colore": "#F59E0B", "finale": False, "ordine": 2},
            {"codice": "SOSPESO", "descrizione": "Sospeso", "colore": "#F59E0B", "finale": False, "ordine": 3},
            {"codice": "COMPLETATO", "descrizione": "Completato", "colore": "#10B981", "finale": True, "ordine": 4},
            {"codice": "ANNULLATO", "descrizione": "Annullato", "colore": "#EF4444", "finale": True, "ordine": 5},
        ]
        for s in stati_intervento:
            exists = db.query(LookupStatiIntervento).filter_by(codice=s["codice"]).first()
            if not exists:
                db.add(LookupStatiIntervento(**s, attivo=True, created_at=datetime.utcnow(), updated_at=datetime.utcnow()))

        # 5. Lookup Tipi Intervento
        print("  - Tipi Intervento")
        tipi_intervento = [
            {"codice": "PRESSO_CLIENTE", "descrizione": "Presso Cliente", "richiede_viaggio": True, "colore": "#8B5CF6", "ordine": 1},
            {"codice": "REMOTO", "descrizione": "Remoto", "richiede_viaggio": False, "colore": "#10B981", "ordine": 2},
            {"codice": "TELEFONICO", "descrizione": "Telefonico", "richiede_viaggio": False, "colore": "#F59E0B", "ordine": 3},
            {"codice": "LABORATORIO", "descrizione": "Laboratorio", "richiede_viaggio": False, "colore": "#3B82F6", "ordine": 4},
            {"codice": "FORMAZIONE", "descrizione": "Formazione", "richiede_viaggio": True, "colore": "#06B6D4", "ordine": 5},
            {"codice": "MANUTENZIONE", "descrizione": "Manutenzione Programmata", "richiede_viaggio": True, "colore": "#6366F1", "ordine": 6},
        ]
        for t in tipi_intervento:
            exists = db.query(LookupTipiIntervento).filter_by(codice=t["codice"]).first()
            if not exists:
                db.add(LookupTipiIntervento(**t, attivo=True, created_at=datetime.utcnow(), updated_at=datetime.utcnow()))

        # 6. Lookup Origini Intervento
        print("  - Origini Intervento")
        origini = [
            {"codice": "DA_TICKET", "descrizione": "Da Ticket", "ordine": 1},
            {"codice": "DA_PIANIFICAZIONE", "descrizione": "Da Pianificazione", "ordine": 2},
            {"codice": "DA_RICHIESTA", "descrizione": "Da Richiesta Diretta", "ordine": 3},
            {"codice": "MANUTENZIONE", "descrizione": "Manutenzione Programmata", "ordine": 4},
        ]
        for o in origini:
            exists = db.query(LookupOriginiIntervento).filter_by(codice=o["codice"]).first()
            if not exists:
                db.add(LookupOriginiIntervento(**o, attivo=True, created_at=datetime.utcnow(), updated_at=datetime.utcnow()))

        # 7. Lookup Categorie Attività
        print("  - Categorie Attività")
        categorie = [
            {"codice": "SUPPORTO", "descrizione": "Supporto Tecnico", "ordine": 1},
            {"codice": "INSTALLAZIONE", "descrizione": "Installazione/Configurazione", "ordine": 2},
            {"codice": "FORMAZIONE", "descrizione": "Formazione", "ordine": 3},
            {"codice": "SVILUPPO", "descrizione": "Sviluppo/Personalizzazione", "ordine": 4},
            {"codice": "MANUTENZIONE", "descrizione": "Manutenzione", "ordine": 5},
            {"codice": "VIAGGIO", "descrizione": "Viaggio/Trasferta", "ordine": 6},
            {"codice": "MATERIALE", "descrizione": "Materiale/Ricambi", "ordine": 7},
        ]
        for c in categorie:
            exists = db.query(LookupCategorieAttivita).filter_by(codice=c["codice"]).first()
            if not exists:
                db.add(LookupCategorieAttivita(**c, attivo=True, created_at=datetime.utcnow(), updated_at=datetime.utcnow()))

        # 8. Lookup Reparti
        print("  - Reparti")
        reparti = [
            {"codice": "HELPDESK", "descrizione": "Help Desk", "ordine": 1},
            {"codice": "SISTEMISTICA", "descrizione": "Sistemistica", "ordine": 2},
            {"codice": "SVILUPPO", "descrizione": "Sviluppo Software", "ordine": 3},
            {"codice": "RETI", "descrizione": "Reti e Infrastrutture", "ordine": 4},
        ]
        for r in reparti:
            exists = db.query(LookupReparti).filter_by(codice=r["codice"]).first()
            if not exists:
                db.add(LookupReparti(**r, attivo=True, created_at=datetime.utcnow(), updated_at=datetime.utcnow()))

        # 9. Lookup Ruoli Utente
        print("  - Ruoli Utente")
        ruoli = [
            {"codice": "ADMIN", "descrizione": "Amministratore", "ordine": 1},
            {"codice": "MANAGER", "descrizione": "Manager", "ordine": 2},
            {"codice": "TECNICO_SENIOR", "descrizione": "Tecnico Senior", "ordine": 3},
            {"codice": "TECNICO", "descrizione": "Tecnico", "ordine": 4},
            {"codice": "USER", "descrizione": "Utente Base", "ordine": 5},
        ]
        for r in ruoli:
            exists = db.query(LookupRuoliUtente).filter_by(codice=r["codice"]).first()
            if not exists:
                db.add(LookupRuoliUtente(**r, attivo=True, created_at=datetime.utcnow(), updated_at=datetime.utcnow()))

        db.commit()
        print("\n✓ Tabelle lookup popolate con successo!")

        # Crea un utente admin di default
        print("\nCreazione utente admin...")
        from app.core.security import get_password_hash

        ruolo_admin = db.query(LookupRuoliUtente).filter_by(codice="ADMIN").first()
        admin_exists = db.query(Tecnico).filter_by(username="admin").first()

        if not admin_exists and ruolo_admin:
            admin = Tecnico(
                username="admin",
                email="admin@daassist.local",
                nome="Admin",
                cognome="System",
                hashed_password=get_password_hash("admin"),
                ruolo_id=ruolo_admin.id,
                attivo=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(admin)
            db.commit()
            print("✓ Utente admin creato (username: admin, password: admin)")
            print("  IMPORTANTE: Cambiare la password al primo accesso!")
        else:
            print("✓ Utente admin già esistente")

    except Exception as e:
        print(f"\n✗ Errore: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    populate_lookups()
