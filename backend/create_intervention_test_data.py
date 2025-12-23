"""
Script to create test intervention data for DAAssist
Run with: docker-compose exec backend python create_intervention_test_data.py
"""
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.user import Tecnico
from app.models.client import CacheClienti
from app.models.intervention import Intervento
from app.models.lookup import (
    LookupTipiIntervento,
    LookupStatiIntervento,
    LookupOriginiIntervento,
)


def create_intervention_test_data():
    db: Session = SessionLocal()

    try:
        print("Creating intervention test data...")

        # Get lookup data
        tipo_cliente = db.query(LookupTipiIntervento).filter_by(codice="CLIENTE").first()
        tipo_remoto = db.query(LookupTipiIntervento).filter_by(codice="REMOTO").first()
        tipo_telefonico = db.query(LookupTipiIntervento).filter_by(codice="TELEFONICO").first()

        stato_pianificato = db.query(LookupStatiIntervento).filter_by(codice="PIANIFICATO").first()
        stato_in_corso = db.query(LookupStatiIntervento).filter_by(codice="IN_CORSO").first()
        stato_completato = db.query(LookupStatiIntervento).filter_by(codice="COMPLETATO").first()

        origine_ticket = db.query(LookupOriginiIntervento).filter_by(codice="DA_TICKET").first()
        origine_pianificazione = db.query(LookupOriginiIntervento).filter_by(codice="DA_PIANIFICAZIONE").first()

        # Get admin user
        admin = db.query(Tecnico).filter_by(username="admin").first()

        # Get clients
        client1 = db.query(CacheClienti).filter_by(codice_gestionale="CLI001").first()
        client2 = db.query(CacheClienti).filter_by(codice_gestionale="CLI002").first()
        client3 = db.query(CacheClienti).filter_by(codice_gestionale="CLI003").first()

        if not all([tipo_cliente, stato_pianificato, origine_ticket, admin, client1]):
            print("ERROR: Missing required lookup data or users/clients")
            print("Please ensure init_db.py and create_test_data.py have been run first")
            return

        # Check if interventions already exist
        existing = db.query(Intervento).first()
        if existing:
            print("Interventions already exist. Skipping creation.")
            return

        print("Creating test interventions...")
        interventi = []

        # Intervention 1 - Cliente, Completato
        int1 = Intervento(
            numero="INT-2024-00001",
            origine_id=origine_pianificazione.id,
            cliente_id=client1.id,
            tipo_intervento_id=tipo_cliente.id,
            stato_id=stato_completato.id,
            tecnico_id=admin.id,
            oggetto="Manutenzione server e backup",
            descrizione_lavoro="Eseguita manutenzione ordinaria server, verifica backup e aggiornamento sistema operativo. Tutti i servizi funzionanti correttamente.",
            note_interne="Cliente molto soddisfatto del servizio.",
            data_inizio=datetime.now() - timedelta(days=5, hours=2),
            data_fine=datetime.now() - timedelta(days=5),
            firma_cliente="[FIRMA_BASE64_SIMULATA]",
            firma_nome="Mario Rossi",
            firma_ruolo="Responsabile IT",
            firma_data=datetime.now() - timedelta(days=5),
            created_at=datetime.now() - timedelta(days=7),
        )
        interventi.append(int1)

        # Intervention 2 - Remoto, In Corso
        int2 = Intervento(
            numero="INT-2024-00002",
            origine_id=origine_ticket.id,
            ticket_id=2,  # Link to ticket TK-2024-00002
            cliente_id=client2.id,
            tipo_intervento_id=tipo_remoto.id,
            stato_id=stato_in_corso.id,
            tecnico_id=admin.id,
            oggetto="Configurazione firewall VPN",
            descrizione_lavoro="Configurazione regole firewall per accesso VPN da remoto.",
            note_interne="Richiede coordinamento con il cliente per test di connessione.",
            data_inizio=datetime.now() - timedelta(hours=1),
            created_at=datetime.now() - timedelta(days=2),
        )
        interventi.append(int2)

        # Intervention 3 - Cliente, Pianificato (futuro)
        int3 = Intervento(
            numero="INT-2024-00003",
            origine_id=origine_pianificazione.id,
            cliente_id=client3.id,
            tipo_intervento_id=tipo_cliente.id,
            stato_id=stato_pianificato.id,
            tecnico_id=admin.id,
            oggetto="Installazione nuove postazioni",
            descrizione_lavoro="Installazione e configurazione 3 nuove postazioni di lavoro complete di software.",
            note_interne="Pianificato per domani mattina ore 9:00.",
            created_at=datetime.now(),
        )
        interventi.append(int3)

        # Intervention 4 - Telefonico, Completato
        int4 = Intervento(
            numero="INT-2024-00004",
            origine_id=origine_ticket.id,
            ticket_id=5,  # Link to ticket TK-2024-00005
            cliente_id=client2.id,
            tipo_intervento_id=tipo_telefonico.id,
            stato_id=stato_completato.id,
            tecnico_id=admin.id,
            oggetto="Reset password utente",
            descrizione_lavoro="Eseguito reset password e guidato utente nella configurazione nuovo accesso. Problema risolto.",
            data_inizio=datetime.now() - timedelta(hours=3),
            data_fine=datetime.now() - timedelta(hours=3) + timedelta(minutes=15),
            firma_cliente="[FIRMA_BASE64_SIMULATA]",
            firma_nome="Paolo Gialli",
            firma_ruolo="Utente",
            firma_data=datetime.now() - timedelta(hours=3) + timedelta(minutes=15),
            created_at=datetime.now() - timedelta(hours=4),
        )
        interventi.append(int4)

        # Intervention 5 - Remoto, Pianificato
        int5 = Intervento(
            numero="INT-2024-00005",
            origine_id=origine_pianificazione.id,
            cliente_id=client1.id,
            tipo_intervento_id=tipo_remoto.id,
            stato_id=stato_pianificato.id,
            tecnico_id=admin.id,
            oggetto="Aggiornamento sistema gestionale",
            descrizione_lavoro="Aggiornamento versione gestionale aziendale e test funzionalità.",
            note_interne="Da coordinare con il cliente per orario fuori produzione.",
            created_at=datetime.now() - timedelta(days=1),
        )
        interventi.append(int5)

        for intervento in interventi:
            db.add(intervento)

        db.commit()
        print(f"Created {len(interventi)} test interventions")

        print("\nInterventions created:")
        for intervento in interventi:
            print(f"  - {intervento.numero}: {intervento.oggetto} [{intervento.stato.descrizione}]")

    except Exception as e:
        print(f"Error creating intervention test data: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    create_intervention_test_data()
