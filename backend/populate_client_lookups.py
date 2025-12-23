#!/usr/bin/env python3
"""
Popola le tabelle lookup per la gestione clienti
"""
from datetime import datetime
from app.database import SessionLocal
from app.models.lookup import LookupStatiCliente, LookupClassificazioniCliente


def populate_stati_cliente():
    """Popola stati cliente"""
    db = SessionLocal()

    stati = [
        {
            "codice": "ATTIVO",
            "descrizione": "Cliente Attivo",
            "colore": "#10B981",
            "ordine": 1
        },
        {
            "codice": "SOSPESO",
            "descrizione": "Cliente Sospeso",
            "colore": "#F59E0B",
            "ordine": 2
        },
        {
            "codice": "INATTIVO",
            "descrizione": "Cliente Inattivo",
            "colore": "#6B7280",
            "ordine": 3
        },
        {
            "codice": "PROSPECT",
            "descrizione": "Prospect (Potenziale Cliente)",
            "colore": "#3B82F6",
            "ordine": 0
        },
    ]

    for stato_data in stati:
        existing = db.query(LookupStatiCliente).filter(
            LookupStatiCliente.codice == stato_data["codice"]
        ).first()

        if not existing:
            stato = LookupStatiCliente(
                **stato_data,
                attivo=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(stato)
            print(f"✓ Aggiunto stato: {stato_data['descrizione']}")
        else:
            print(f"- Stato già esistente: {stato_data['descrizione']}")

    db.commit()
    db.close()


def populate_classificazioni_cliente():
    """Popola classificazioni cliente"""
    db = SessionLocal()

    classificazioni = [
        {
            "codice": "VIP",
            "descrizione": "Cliente VIP",
            "colore": "#8B5CF6",
            "ordine": 1
        },
        {
            "codice": "PREMIUM",
            "descrizione": "Cliente Premium",
            "colore": "#EC4899",
            "ordine": 2
        },
        {
            "codice": "STANDARD",
            "descrizione": "Cliente Standard",
            "colore": "#3B82F6",
            "ordine": 3
        },
        {
            "codice": "BASIC",
            "descrizione": "Cliente Basic",
            "colore": "#6B7280",
            "ordine": 4
        },
        {
            "codice": "ENTERPRISE",
            "descrizione": "Enterprise",
            "colore": "#059669",
            "ordine": 0
        },
    ]

    for class_data in classificazioni:
        existing = db.query(LookupClassificazioniCliente).filter(
            LookupClassificazioniCliente.codice == class_data["codice"]
        ).first()

        if not existing:
            classificazione = LookupClassificazioniCliente(
                **class_data,
                attivo=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(classificazione)
            print(f"✓ Aggiunta classificazione: {class_data['descrizione']}")
        else:
            print(f"- Classificazione già esistente: {class_data['descrizione']}")

    db.commit()
    db.close()


if __name__ == "__main__":
    print("🔧 Populating client lookup tables...")
    print("\n📊 Stati Cliente:")
    populate_stati_cliente()
    print("\n📊 Classificazioni Cliente:")
    populate_classificazioni_cliente()
    print("\n✅ Done!")
