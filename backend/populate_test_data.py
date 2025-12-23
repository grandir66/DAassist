"""
Script per popolare il database con dati di prova
"""
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.client import CacheClienti, SediCliente, CacheReferenti
from datetime import datetime
import json

def populate_test_data():
    db = SessionLocal()

    try:
        print("🚀 Popolamento dati di prova...")

        # Clienti di prova
        clienti_data = [
            {
                "codice_gestionale": "CLI001",
                "ragione_sociale": "TechSolution S.r.l.",
                "partita_iva": "IT12345678901",
                "codice_fiscale": "12345678901",
                "indirizzo": "Via Roma 123",
                "cap": "20100",
                "citta": "Milano",
                "provincia": "MI",
                "telefono": "02-12345678",
                "email": "info@techsolution.it",
                "pec": "techsolution@pec.it",
                "stato_cliente": "ATTIVO",
                "classificazione": "PREMIUM",
                "orari_servizio": json.dumps({
                    "lunedi": {"inizio": "09:00", "fine": "18:00"},
                    "martedi": {"inizio": "09:00", "fine": "18:00"},
                    "mercoledi": {"inizio": "09:00", "fine": "18:00"},
                    "giovedi": {"inizio": "09:00", "fine": "18:00"},
                    "venerdi": {"inizio": "09:00", "fine": "18:00"}
                }),
                "nomi_alternativi": "Tech Solution, TechSolution, TS",
                "note": "Cliente storico, contratto annuale premium con SLA 4h",
                "ultimo_sync": datetime.now(),
                "attivo": 1
            },
            {
                "codice_gestionale": "CLI002",
                "ragione_sociale": "Studio Commerciale Rossi & Associati",
                "partita_iva": "IT98765432109",
                "codice_fiscale": "98765432109",
                "indirizzo": "Corso Italia 45",
                "cap": "00100",
                "citta": "Roma",
                "provincia": "RM",
                "telefono": "06-98765432",
                "email": "info@studiorossi.it",
                "pec": "studiorossi@pec.it",
                "stato_cliente": "ATTIVO",
                "classificazione": "STANDARD",
                "orari_servizio": json.dumps({
                    "lunedi": {"inizio": "08:30", "fine": "17:30"},
                    "martedi": {"inizio": "08:30", "fine": "17:30"},
                    "mercoledi": {"inizio": "08:30", "fine": "17:30"},
                    "giovedi": {"inizio": "08:30", "fine": "17:30"},
                    "venerdi": {"inizio": "08:30", "fine": "13:00"}
                }),
                "nomi_alternativi": "Studio Rossi",
                "note": "Assistenza ordinaria, chiuso il pomeriggio del venerdì",
                "ultimo_sync": datetime.now(),
                "attivo": 1
            },
            {
                "codice_gestionale": "CLI003",
                "ragione_sociale": "Industrie Manifatturiere Beta S.p.A.",
                "partita_iva": "IT11223344556",
                "codice_fiscale": "11223344556",
                "indirizzo": "Via Industriale 67",
                "cap": "10100",
                "citta": "Torino",
                "provincia": "TO",
                "telefono": "011-1234567",
                "email": "it@beta-manifatture.it",
                "pec": "betamanifatture@pec.it",
                "stato_cliente": "ATTIVO",
                "classificazione": "ENTERPRISE",
                "orari_servizio": json.dumps({
                    "lunedi": {"inizio": "06:00", "fine": "22:00"},
                    "martedi": {"inizio": "06:00", "fine": "22:00"},
                    "mercoledi": {"inizio": "06:00", "fine": "22:00"},
                    "giovedi": {"inizio": "06:00", "fine": "22:00"},
                    "venerdi": {"inizio": "06:00", "fine": "22:00"},
                    "sabato": {"inizio": "08:00", "fine": "14:00"}
                }),
                "nomi_alternativi": "Beta, Manifatture Beta, Beta Manifatture",
                "note": "Grande azienda con 3 sedi operative, contratto enterprise H24",
                "ultimo_sync": datetime.now(),
                "attivo": 1
            },
            {
                "codice_gestionale": "CLI004",
                "ragione_sociale": "Startup Innovativa Alpha",
                "partita_iva": "IT55667788990",
                "codice_fiscale": "55667788990",
                "indirizzo": "Via Startup 12",
                "cap": "50100",
                "citta": "Firenze",
                "provincia": "FI",
                "telefono": "055-9876543",
                "email": "hello@alpha-startup.io",
                "stato_cliente": "PROSPECT",
                "classificazione": "BASIC",
                "note": "Prospect interessato, in valutazione contratto base",
                "nomi_alternativi": "Alpha, Alpha Startup",
                "ultimo_sync": datetime.now(),
                "attivo": 1
            },
            {
                "codice_gestionale": "CLI005",
                "ragione_sociale": "Hotel Continental",
                "partita_iva": "IT33221144556",
                "codice_fiscale": "33221144556",
                "indirizzo": "Lungomare 88",
                "cap": "80100",
                "citta": "Napoli",
                "provincia": "NA",
                "telefono": "081-5555555",
                "email": "info@hotelcontinental.it",
                "pec": "hotelcontinental@pec.it",
                "stato_cliente": "SOSPESO",
                "classificazione": "STANDARD",
                "note": "Servizio sospeso per morosità, in attesa di rinnovo",
                "nomi_alternativi": "Hotel Continental, Continental",
                "ultimo_sync": datetime.now(),
                "attivo": 1
            }
        ]

        clienti = []
        for cliente_data in clienti_data:
            cliente = CacheClienti(**cliente_data)
            db.add(cliente)
            clienti.append(cliente)

        db.flush()  # Get IDs
        print(f"✅ Creati {len(clienti)} clienti")

        # Sedi operative per Beta Manifatture (cliente 3)
        beta = clienti[2]
        sedi_data = [
            {
                "cliente_id": beta.id,
                "nome_sede": "Sede Produzione Nord",
                "codice_sede": "PROD-NORD",
                "indirizzo": "Via Industriale 67",
                "cap": "10100",
                "citta": "Torino",
                "provincia": "TO",
                "telefono": "011-1234567",
                "email": "produzione.nord@beta-manifatture.it",
                "orari_servizio": json.dumps({
                    "lunedi": {"inizio": "06:00", "fine": "22:00"},
                    "martedi": {"inizio": "06:00", "fine": "22:00"},
                    "mercoledi": {"inizio": "06:00", "fine": "22:00"},
                    "giovedi": {"inizio": "06:00", "fine": "22:00"},
                    "venerdi": {"inizio": "06:00", "fine": "22:00"}
                }),
                "note": "Sede principale con linea produttiva 1 e 2",
                "attivo": 1
            },
            {
                "cliente_id": beta.id,
                "nome_sede": "Magazzino Logistica",
                "codice_sede": "LOG-TO",
                "indirizzo": "Via Logistica 34",
                "cap": "10150",
                "citta": "Torino",
                "provincia": "TO",
                "telefono": "011-7654321",
                "email": "logistica@beta-manifatture.it",
                "orari_servizio": json.dumps({
                    "lunedi": {"inizio": "07:00", "fine": "19:00"},
                    "martedi": {"inizio": "07:00", "fine": "19:00"},
                    "mercoledi": {"inizio": "07:00", "fine": "19:00"},
                    "giovedi": {"inizio": "07:00", "fine": "19:00"},
                    "venerdi": {"inizio": "07:00", "fine": "19:00"}
                }),
                "note": "Magazzino e centro distribuzione",
                "attivo": 1
            },
            {
                "cliente_id": beta.id,
                "nome_sede": "Uffici Direzione Milano",
                "codice_sede": "DIR-MI",
                "indirizzo": "Corso Buenos Aires 123",
                "cap": "20100",
                "citta": "Milano",
                "provincia": "MI",
                "telefono": "02-9998877",
                "email": "direzione@beta-manifatture.it",
                "orari_servizio": json.dumps({
                    "lunedi": {"inizio": "09:00", "fine": "18:00"},
                    "martedi": {"inizio": "09:00", "fine": "18:00"},
                    "mercoledi": {"inizio": "09:00", "fine": "18:00"},
                    "giovedi": {"inizio": "09:00", "fine": "18:00"},
                    "venerdi": {"inizio": "09:00", "fine": "18:00"}
                }),
                "note": "Direzione generale e uffici amministrativi",
                "attivo": 1
            }
        ]

        # Sedi per TechSolution
        tech = clienti[0]
        sedi_data.extend([
            {
                "cliente_id": tech.id,
                "nome_sede": "Sede Operativa Roma",
                "codice_sede": "TECH-RM",
                "indirizzo": "Via Tiburtina 456",
                "cap": "00100",
                "citta": "Roma",
                "provincia": "RM",
                "telefono": "06-11223344",
                "email": "roma@techsolution.it",
                "note": "Sede secondaria per assistenza centro-sud",
                "attivo": 1
            }
        ])

        sedi = []
        for sede_data in sedi_data:
            sede = SediCliente(**sede_data)
            db.add(sede)
            sedi.append(sede)

        db.flush()
        print(f"✅ Create {len(sedi)} sedi operative")

        # Referenti/Contatti
        referenti_data = [
            # TechSolution
            {
                "cliente_id": tech.id,
                "sede_id": None,
                "nome": "Marco",
                "cognome": "Bianchi",
                "ruolo": "Responsabile IT",
                "telefono": "02-12345678",
                "cellulare": "335-1234567",
                "interno_telefonico": "201",
                "email": "m.bianchi@techsolution.it",
                "contatto_principale": 1,
                "riceve_notifiche": 1,
                "referente_it": 1,
                "note": "Referente principale per tutte le problematiche IT",
                "ultimo_sync": datetime.now(),
                "attivo": 1
            },
            {
                "cliente_id": tech.id,
                "sede_id": None,
                "nome": "Laura",
                "cognome": "Verdi",
                "ruolo": "Amministratore Delegato",
                "telefono": "02-12345678",
                "cellulare": "340-7654321",
                "interno_telefonico": "101",
                "email": "l.verdi@techsolution.it",
                "contatto_principale": 0,
                "riceve_notifiche": 1,
                "referente_it": 0,
                "note": "Da contattare solo per emergenze",
                "ultimo_sync": datetime.now(),
                "attivo": 1
            },
            {
                "cliente_id": tech.id,
                "sede_id": sedi[3].id,  # Sede Roma
                "nome": "Paolo",
                "cognome": "Russo",
                "ruolo": "Tecnico Informatico",
                "telefono": "06-11223344",
                "cellulare": "328-9876543",
                "email": "p.russo@techsolution.it",
                "contatto_principale": 0,
                "riceve_notifiche": 1,
                "referente_it": 1,
                "note": "Responsabile sede di Roma",
                "ultimo_sync": datetime.now(),
                "attivo": 1
            },
            # Studio Rossi
            {
                "cliente_id": clienti[1].id,
                "sede_id": None,
                "nome": "Giuseppe",
                "cognome": "Rossi",
                "ruolo": "Commercialista",
                "telefono": "06-98765432",
                "cellulare": "339-1122334",
                "interno_telefonico": "11",
                "email": "g.rossi@studiorossi.it",
                "contatto_principale": 1,
                "riceve_notifiche": 1,
                "referente_it": 0,
                "ultimo_sync": datetime.now(),
                "attivo": 1
            },
            {
                "cliente_id": clienti[1].id,
                "sede_id": None,
                "nome": "Anna",
                "cognome": "Ferrari",
                "ruolo": "Segretaria",
                "telefono": "06-98765432",
                "cellulare": "347-5544332",
                "interno_telefonico": "10",
                "email": "a.ferrari@studiorossi.it",
                "contatto_principale": 0,
                "riceve_notifiche": 1,
                "referente_it": 1,
                "note": "Si occupa di problemi IT e ordini materiali",
                "ultimo_sync": datetime.now(),
                "attivo": 1
            },
            # Beta Manifatture
            {
                "cliente_id": beta.id,
                "sede_id": sedi[0].id,  # Produzione Nord
                "nome": "Roberto",
                "cognome": "Colombo",
                "ruolo": "CIO - Chief Information Officer",
                "telefono": "011-1234567",
                "cellulare": "335-9988776",
                "interno_telefonico": "300",
                "email": "r.colombo@beta-manifatture.it",
                "contatto_principale": 1,
                "riceve_notifiche": 1,
                "referente_it": 1,
                "note": "Responsabile IT di gruppo, da contattare sempre",
                "ultimo_sync": datetime.now(),
                "attivo": 1
            },
            {
                "cliente_id": beta.id,
                "sede_id": sedi[0].id,  # Produzione Nord
                "nome": "Stefano",
                "cognome": "Moretti",
                "ruolo": "Responsabile Produzione",
                "telefono": "011-1234567",
                "cellulare": "340-1122334",
                "interno_telefonico": "150",
                "email": "s.moretti@beta-manifatture.it",
                "contatto_principale": 0,
                "riceve_notifiche": 1,
                "referente_it": 0,
                "ultimo_sync": datetime.now(),
                "attivo": 1
            },
            {
                "cliente_id": beta.id,
                "sede_id": sedi[1].id,  # Logistica
                "nome": "Francesca",
                "cognome": "Ricci",
                "ruolo": "Responsabile Magazzino",
                "telefono": "011-7654321",
                "cellulare": "328-7766554",
                "interno_telefonico": "180",
                "email": "f.ricci@beta-manifatture.it",
                "contatto_principale": 0,
                "riceve_notifiche": 1,
                "referente_it": 0,
                "ultimo_sync": datetime.now(),
                "attivo": 1
            },
            {
                "cliente_id": beta.id,
                "sede_id": sedi[1].id,  # Logistica
                "nome": "Andrea",
                "cognome": "Esposito",
                "ruolo": "Sistemista",
                "telefono": "011-7654321",
                "cellulare": "335-4455667",
                "email": "a.esposito@beta-manifatture.it",
                "contatto_principale": 0,
                "riceve_notifiche": 1,
                "referente_it": 1,
                "note": "Tecnico IT sede logistica",
                "ultimo_sync": datetime.now(),
                "attivo": 1
            },
            {
                "cliente_id": beta.id,
                "sede_id": sedi[2].id,  # Direzione Milano
                "nome": "Giulia",
                "cognome": "Romano",
                "ruolo": "Direttore Generale",
                "telefono": "02-9998877",
                "cellulare": "340-9988776",
                "interno_telefonico": "100",
                "email": "g.romano@beta-manifatture.it",
                "contatto_principale": 0,
                "riceve_notifiche": 0,
                "referente_it": 0,
                "note": "Contattare solo per escalation critiche",
                "ultimo_sync": datetime.now(),
                "attivo": 1
            },
            {
                "cliente_id": beta.id,
                "sede_id": sedi[2].id,  # Direzione Milano
                "nome": "Luca",
                "cognome": "Gallo",
                "ruolo": "IT Manager Milano",
                "telefono": "02-9998877",
                "cellulare": "335-3344556",
                "interno_telefonico": "310",
                "email": "l.gallo@beta-manifatture.it",
                "contatto_principale": 0,
                "riceve_notifiche": 1,
                "referente_it": 1,
                "note": "Referente IT per sede Milano",
                "ultimo_sync": datetime.now(),
                "attivo": 1
            },
            # Alpha Startup
            {
                "cliente_id": clienti[3].id,
                "sede_id": None,
                "nome": "Matteo",
                "cognome": "Costa",
                "ruolo": "CEO & Founder",
                "telefono": "055-9876543",
                "cellulare": "340-1234567",
                "email": "m.costa@alpha-startup.io",
                "contatto_principale": 1,
                "riceve_notifiche": 1,
                "referente_it": 1,
                "note": "Nella startup si occupa anche di IT",
                "ultimo_sync": datetime.now(),
                "attivo": 1
            },
            # Hotel Continental
            {
                "cliente_id": clienti[4].id,
                "sede_id": None,
                "nome": "Carla",
                "cognome": "Fontana",
                "ruolo": "Direttore Hotel",
                "telefono": "081-5555555",
                "cellulare": "339-6677889",
                "interno_telefonico": "1",
                "email": "c.fontana@hotelcontinental.it",
                "contatto_principale": 1,
                "riceve_notifiche": 1,
                "referente_it": 0,
                "ultimo_sync": datetime.now(),
                "attivo": 1
            },
            {
                "cliente_id": clienti[4].id,
                "sede_id": None,
                "nome": "Davide",
                "cognome": "Serra",
                "ruolo": "Receptionist",
                "telefono": "081-5555555",
                "interno_telefonico": "2",
                "email": "reception@hotelcontinental.it",
                "contatto_principale": 0,
                "riceve_notifiche": 0,
                "referente_it": 1,
                "note": "Gestisce i problemi IT di reception",
                "ultimo_sync": datetime.now(),
                "attivo": 1
            }
        ]

        referenti = []
        for ref_data in referenti_data:
            referente = CacheReferenti(**ref_data)
            db.add(referente)
            referenti.append(referente)

        db.flush()
        print(f"✅ Creati {len(referenti)} referenti/contatti")

        # Aggiorna referente_it_id per i clienti
        tech.referente_it_id = referenti[0].id  # Marco Bianchi
        clienti[1].referente_it_id = referenti[4].id  # Anna Ferrari (Studio Rossi)
        beta.referente_it_id = referenti[5].id  # Roberto Colombo (Beta)
        clienti[3].referente_it_id = referenti[11].id  # Matteo Costa (Alpha)
        clienti[4].referente_it_id = referenti[13].id  # Davide Serra (Hotel)

        db.commit()
        print("✅ Aggiornati referenti IT principali per i clienti")

        print("\n" + "="*60)
        print("✅ DATI DI PROVA CARICATI CON SUCCESSO!")
        print("="*60)
        print(f"\n📊 Riepilogo:")
        print(f"   • {len(clienti)} clienti")
        print(f"   • {len(sedi)} sedi operative")
        print(f"   • {len(referenti)} contatti/referenti")
        print(f"\n🎯 Clienti creati:")
        for cliente in clienti:
            print(f"   • {cliente.ragione_sociale} ({cliente.stato_cliente} - {cliente.classificazione})")

    except Exception as e:
        print(f"❌ Errore: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    populate_test_data()
