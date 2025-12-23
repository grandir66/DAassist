"""
Script to create test data for DAAssist
Run with: docker-compose exec backend python create_test_data.py
"""
import sys
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.user import Tecnico
from app.models.client import CacheClienti
from app.models.ticket import Ticket
from app.models.lookup import (
    LookupCanaliRichiesta,
    LookupPriorita,
    LookupStatiTicket,
)


def create_test_data():
    db: Session = SessionLocal()

    try:
        print("Creating test data...")

        # Get lookup data
        canale_email = db.query(LookupCanaliRichiesta).filter_by(codice="EMAIL").first()
        canale_telefono = db.query(LookupCanaliRichiesta).filter_by(codice="TELEFONO").first()
        canale_portale = db.query(LookupCanaliRichiesta).filter_by(codice="WEBAPP").first()

        priorita_critica = db.query(LookupPriorita).filter_by(codice="CRITICA").first()
        priorita_alta = db.query(LookupPriorita).filter_by(codice="ALTA").first()
        priorita_normale = db.query(LookupPriorita).filter_by(codice="NORMALE").first()
        priorita_bassa = db.query(LookupPriorita).filter_by(codice="BASSA").first()

        stato_nuovo = db.query(LookupStatiTicket).filter_by(codice="NUOVO").first()
        stato_preso_carico = db.query(LookupStatiTicket).filter_by(codice="PRESO_CARICO").first()
        stato_in_lavorazione = db.query(LookupStatiTicket).filter_by(codice="IN_LAVORAZIONE").first()
        stato_chiuso = db.query(LookupStatiTicket).filter_by(codice="CHIUSO").first()

        # Get admin user
        admin = db.query(Tecnico).filter_by(username="admin").first()

        # Create test clients
        print("Creating test clients...")
        clients = []

        # Check if clients already exist
        existing_client1 = db.query(CacheClienti).filter_by(codice_gestionale="CLI001").first()
        if existing_client1:
            print("Clients already exist, using existing ones...")
            client1 = existing_client1
            client2 = db.query(CacheClienti).filter_by(codice_gestionale="CLI002").first()
            client3 = db.query(CacheClienti).filter_by(codice_gestionale="CLI003").first()
        else:
            client1 = CacheClienti(
                codice_gestionale="CLI001",
                ragione_sociale="Acme S.r.l.",
                partita_iva="12345678901",
                codice_fiscale="12345678901",
                indirizzo="Via Roma 1",
                citta="Milano",
                provincia="MI",
                cap="20100",
                telefono="+39 02 1234567",
                email="info@acme.it",
                ultimo_sync=datetime.now(),
                attivo=True,
            )
            clients.append(client1)

            client2 = CacheClienti(
                codice_gestionale="CLI002",
                ragione_sociale="Beta Corporation S.p.A.",
                partita_iva="98765432109",
                codice_fiscale="98765432109",
                indirizzo="Corso Italia 100",
                citta="Roma",
                provincia="RM",
                cap="00100",
                telefono="+39 06 9876543",
                email="contatti@beta.it",
                ultimo_sync=datetime.now(),
                attivo=True,
            )
            clients.append(client2)

            client3 = CacheClienti(
                codice_gestionale="CLI003",
                ragione_sociale="Gamma Technologies Ltd",
                partita_iva="11223344556",
                codice_fiscale="11223344556",
                indirizzo="Piazza Duomo 5",
                citta="Torino",
                provincia="TO",
                cap="10100",
                telefono="+39 011 1122334",
                email="support@gamma.it",
                ultimo_sync=datetime.now(),
                attivo=True,
            )
            clients.append(client3)

            for client in clients:
                db.add(client)

            db.commit()
            print(f"Created {len(clients)} test clients")

        # Create test tickets
        print("Creating test tickets...")
        tickets = []

        # Ticket 1 - Critical, New
        ticket1 = Ticket(
            numero="TK-2024-00001",
            oggetto="Server principale non risponde - Sistema down",
            descrizione="Il server principale non risponde da 30 minuti. Tutti i dipendenti non possono accedere ai sistemi aziendali. Necessario intervento immediato.",
            cliente_id=client1.id,
            priorita_id=priorita_critica.id,
            stato_id=stato_nuovo.id,
            canale_id=canale_telefono.id,
            referente_nome="Mario Rossi",
            created_at=datetime.now() - timedelta(hours=2),
        )
        tickets.append(ticket1)

        # Ticket 2 - High, In progress
        ticket2 = Ticket(
            numero="TK-2024-00002",
            oggetto="Problemi con configurazione firewall",
            descrizione="Dopo l'ultimo aggiornamento del firewall, alcuni servizi non sono più raggiungibili dall'esterno.",
            cliente_id=client2.id,
            priorita_id=priorita_alta.id,
            stato_id=stato_in_lavorazione.id,
            canale_id=canale_email.id,
            tecnico_assegnato_id=admin.id,
            referente_nome="Laura Bianchi",
            created_at=datetime.now() - timedelta(hours=5),
        )
        tickets.append(ticket2)

        # Ticket 3 - Normal, Taken
        ticket3 = Ticket(
            numero="TK-2024-00003",
            oggetto="Installazione nuovo software gestionale",
            descrizione="Richiesta installazione e configurazione software gestionale su 5 postazioni.",
            cliente_id=client1.id,
            priorita_id=priorita_normale.id,
            stato_id=stato_preso_carico.id,
            canale_id=canale_portale.id,
            tecnico_assegnato_id=admin.id,
            referente_nome="Giuseppe Verdi",
            created_at=datetime.now() - timedelta(days=1),
        )
        tickets.append(ticket3)

        # Ticket 4 - Low, New
        ticket4 = Ticket(
            numero="TK-2024-00004",
            oggetto="Stampante ufficio 3° piano non stampa",
            descrizione="La stampante HP nell'ufficio del 3° piano non risponde ai comandi di stampa.",
            cliente_id=client3.id,
            priorita_id=priorita_bassa.id,
            stato_id=stato_nuovo.id,
            canale_id=canale_email.id,
            referente_nome="Anna Neri",
            created_at=datetime.now() - timedelta(hours=8),
        )
        tickets.append(ticket4)

        # Ticket 5 - Normal, New
        ticket5 = Ticket(
            numero="TK-2024-00005",
            oggetto="Reset password utente amministrativo",
            descrizione="L'utente ha dimenticato la password e non riesce più ad accedere al sistema.",
            cliente_id=client2.id,
            priorita_id=priorita_normale.id,
            stato_id=stato_nuovo.id,
            canale_id=canale_telefono.id,
            referente_nome="Paolo Gialli",
            created_at=datetime.now() - timedelta(hours=1),
        )
        tickets.append(ticket5)

        # Ticket 6 - Closed today
        ticket6 = Ticket(
            numero="TK-2024-00006",
            oggetto="Backup non funzionante",
            descrizione="Il backup notturno non viene eseguito correttamente da 3 giorni.",
            cliente_id=client1.id,
            priorita_id=priorita_alta.id,
            stato_id=stato_chiuso.id,
            canale_id=canale_email.id,
            tecnico_assegnato_id=admin.id,
            referente_nome="Stefano Blu",
            data_chiusura=datetime.now(),
            tipo_chiusura="RISOLTO",
            note_chiusura="Problema risolto: configurazione backup corretta.",
            created_at=datetime.now() - timedelta(days=2),
        )
        tickets.append(ticket6)

        # Ticket 7 - Closed yesterday
        ticket7 = Ticket(
            numero="TK-2024-00007",
            oggetto="Richiesta nuova licenza Office",
            descrizione="Necessaria licenza Microsoft Office per nuovo dipendente.",
            cliente_id=client3.id,
            priorita_id=priorita_normale.id,
            stato_id=stato_chiuso.id,
            canale_id=canale_portale.id,
            tecnico_assegnato_id=admin.id,
            referente_nome="Chiara Rosa",
            data_chiusura=datetime.now() - timedelta(days=1),
            tipo_chiusura="RISOLTO",
            note_chiusura="Licenza acquistata e attivata.",
            created_at=datetime.now() - timedelta(days=3),
        )
        tickets.append(ticket7)

        for ticket in tickets:
            db.add(ticket)

        db.commit()
        print(f"Created {len(tickets)} test tickets")

        print("\nTest data created successfully!")
        print("\nTickets created:")
        for ticket in tickets:
            print(f"  - {ticket.numero}: {ticket.oggetto} [{ticket.priorita.descrizione}] [{ticket.stato.descrizione}]")

    except Exception as e:
        print(f"Error creating test data: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    create_test_data()
