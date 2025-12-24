#!/bin/bash
# Script per inizializzare il database

echo "Inizializzazione database DAAssist..."

# Esegui le migrazioni Alembic
docker exec daassist-backend alembic upgrade head

# Crea utente admin di default
docker exec daassist-backend python -c "
from app.database import SessionLocal
from app.models.tecnico import Tecnico
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
db = SessionLocal()

# Controlla se admin esiste già
admin = db.query(Tecnico).filter(Tecnico.username == 'admin').first()
if not admin:
    admin = Tecnico(
        username='admin',
        email='admin@daassist.local',
        nome='Admin',
        cognome='Sistema',
        password_hash=pwd_context.hash('admin'),
        attivo=True
    )
    db.add(admin)
    db.commit()
    print('✓ Utente admin creato (username: admin, password: admin)')
else:
    print('✓ Utente admin già esistente')

db.close()
"

echo "✓ Database inizializzato"
