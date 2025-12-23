# DAAssist - Changelog

## [Unreleased] - 2025-12-18

### Aggiunto
- ✅ **Gestione Tecnici completa** (CRUD)
  - Creazione, modifica, eliminazione (soft delete) tecnici
  - Filtri avanzati: ricerca, reparto, ruolo, stato
  - Toggle attivo/disattivato
  - Campi LDAP per integrazione Active Directory/LDAP
    - `ldap_dn`: Distinguished Name per autenticazione
    - `ldap_enabled`: Flag abilitazione autenticazione LDAP
  - Indicatore visivo LDAP nella lista tecnici
  - Colore calendario personalizzato per ciascun tecnico
  - Gestione notifiche (email/push)

- ✅ **API Contratti** (backend completo)
  - CRUD endpoints per gestione contratti
  - Filtri: cliente, tipo, scaduti, attivi
  - Statistiche contratti per cliente (ore incluse/utilizzate)
  - Collegamento a SLA
  - Gestione ore residue

- ✅ **Script di utilità**
  - `start.sh`: Avvio automatico backend + frontend
  - `stop.sh`: Arresto servizi
  - `db-shell.sh`: Accesso rapido database PostgreSQL
  - `db-queries.sql`: Collezione query SQL utili
  - `db-inspect.sh`: Ispezione database con statistiche

- ✅ **File .cursorrules**
  - Regole complete per sviluppo in Cursor AI
  - Pattern architetturali
  - Convenzioni di naming
  - Best practices Python 3.9 e React/TypeScript

- ✅ **Struttura Clienti estesa** (modelli database)
  - Nuova tabella `sedi_cliente`: Gestione sedi operative multiple
    - nome_sede, codice_sede, indirizzo completo
    - contatti sede (telefono, email)
    - orari_servizio specifici per sede
  - Estensione tabella `cache_clienti`:
    - `stato_cliente`: ATTIVO, SOSPESO, INATTIVO, PROSPECT (con lookup)
    - `classificazione`: VIP, PREMIUM, STANDARD, BASIC, ENTERPRISE (con lookup)
    - `referente_it_id`: Collegamento a referente IT principale
    - `orari_servizio`: JSON con orari per ogni giorno settimana
    - `nomi_alternativi`: Nomi/acronimi alternativi per ricerca
  - Estensione tabella `cache_referenti` (rubrica):
    - `sede_id`: Collegamento alla sede di appartenenza
    - `interno_telefonico`: Numero interno centralino
    - `referente_it`: Flag identificativo referente IT
    - `note`: Note aggiuntive sul contatto
    - Indici su nome, cognome, email per ricerca veloce
  - Tabelle lookup cliente:
    - `lookup_stati_cliente`: 4 stati con colori
    - `lookup_classificazioni_cliente`: 5 livelli con colori
  - Script `populate_client_lookups.py`: Popolamento dati lookup

### Modificato
- 🔧 Form tecnici uniformato ai campi database (completato)
  - Aggiunti campi LDAP: `ldap_dn`, `ldap_enabled`, `username_ad`
  - Aggiunti campi contatti: `cellulare`, `interno_telefonico`, `telegram_id`
  - Aggiunti campi organizzazione: `codice_tecnico`, `note`
  - Sezioni organizzate: Dati personali, Contatti, Organizzazione, LDAP/AD, Notifiche, Note
  - Colonna LDAP nella tabella tecnici
  - Migration database per nuovi campi applicata

- 🔧 Fix compatibilità Python 3.9
  - Convertito syntax `str | None` → `Optional[str]`
  - Aggiunto import `from typing import Optional, List`
  - Installato `email-validator` per Pydantic EmailStr

- 🔧 Fix dashboard repository
  - Corretto filtro `finale` da boolean a integer (0/1)

### Fix
- 🐛 Import errato in `contracts.py` (SLADefinizione)
- 🐛 SQL Server connection resa opzionale
- 🐛 Circular FK dependencies risolte con `use_alter=True`

## Database

### Tabelle (40 totali)
- `tecnici` - Utenti tecnici (18 campi)
- `ticket` - Gestione ticket (27 campi)
- `interventi` - Gestione interventi (18 campi)
- `cache_clienti` - Cache clienti dal gestionale
- `cache_contratti` - Contratti clienti
- `cache_referenti` - Referenti clienti
- 9 tabelle `lookup_*` - Dati configurazione
- Tabelle KB, Asset, Calendario, SLA

### Credenziali Database
```
Database: daassist
Host: localhost
Port: 5432
User: postgres (o daassist_user)
Password: daassist_password
```

### Utente Admin Default
```
Username: admin
Password: admin
⚠️ Cambiare al primo accesso!
```

## Tecnologie

### Backend
- FastAPI 0.109+
- Python 3.9 (strict compatibility)
- PostgreSQL 14
- SQLAlchemy 2.0
- Alembic migrations
- JWT authentication
- Pydantic v2 validation

### Frontend
- React 18 + TypeScript
- Vite 5.x
- React Router v6
- Zustand (state management)
- Axios (HTTP client)
- TailwindCSS 3.x
- Lucide React (icons)

## Endpoints API Disponibili

### Authentication
- `POST /api/v1/auth/login` - Login
- `GET /api/v1/auth/me` - Info utente corrente
- `GET /api/v1/auth/tecnici` - Lista tecnici

### Tecnici
- `GET /api/v1/technicians` - Lista tecnici
- `GET /api/v1/technicians/{id}` - Dettaglio tecnico
- `POST /api/v1/technicians` - Crea tecnico
- `PUT /api/v1/technicians/{id}` - Aggiorna tecnico
- `DELETE /api/v1/technicians/{id}` - Disattiva tecnico

### Contratti (solo backend)
- `GET /api/v1/contracts` - Lista contratti
- `GET /api/v1/contracts/{id}` - Dettaglio contratto
- `POST /api/v1/contracts` - Crea contratto
- `PUT /api/v1/contracts/{id}` - Aggiorna contratto
- `DELETE /api/v1/contracts/{id}` - Disattiva contratto
- `GET /api/v1/contracts/stats/by-client/{id}` - Statistiche

### Tickets
- `GET /api/v1/tickets` - Lista ticket
- `GET /api/v1/tickets/{id}` - Dettaglio ticket
- `POST /api/v1/tickets` - Crea ticket
- `PUT /api/v1/tickets/{id}` - Aggiorna ticket
- Endpoints per chiusura, note, messaggi, allegati

### Interventi
- `GET /api/v1/interventions` - Lista interventi
- `GET /api/v1/interventions/{id}` - Dettaglio intervento
- `POST /api/v1/interventions` - Crea intervento
- `POST /api/v1/interventions/{id}/start` - Avvia intervento
- `POST /api/v1/interventions/{id}/complete` - Completa intervento

### Lookup Tables
- `GET /api/v1/lookup/channels` - Canali richiesta
- `GET /api/v1/lookup/priorities` - Priorità
- `GET /api/v1/lookup/ticket-states` - Stati ticket
- `GET /api/v1/lookup/intervention-states` - Stati intervento
- `GET /api/v1/lookup/intervention-types` - Tipi intervento
- `GET /api/v1/lookup/activity-categories` - Categorie attività
- `GET /api/v1/lookup/departments` - Reparti
- `GET /api/v1/lookup/user-roles` - Ruoli utente

## TODO

### Frontend da Implementare
- [ ] Pagina gestione Contratti (backend già pronto)
- [ ] Gestione Clienti - aggiungere creazione
- [ ] Gestione Categorie Attività / Tipi di Servizio
- [ ] Voce menu per Contratti

### Features Future
- [ ] Calendario eventi
- [ ] Gestione Asset
- [ ] Knowledge Base
- [ ] Report e statistiche avanzate
- [ ] Dashboard personalizzabile
- [ ] Notifiche real-time
- [ ] Export dati (PDF, Excel)
- [ ] Integrazione Email
- [ ] API sincronizzazione gestionale

## Note di Sviluppo

- Usare sempre Python 3.9 compatible syntax
- Boolean in DB sono `Integer` (0/1) non `Boolean`
- Soft delete: `attivo = False` invece di DELETE
- Pydantic: `from_attributes = True` (non `orm_mode`)
- Relationship lazy="joined" per dati sempre necessari
- Foreign Keys con `index=True` per performance
- Paginazione default: page=1, limit=50

## Comandi Utili

```bash
# Avvio applicazione
./start.sh

# Stop applicazione
./stop.sh

# Accesso database
./db-shell.sh

# Migration database
cd backend
alembic revision --autogenerate -m "descrizione"
alembic upgrade head

# Populate lookup data
cd backend
python3 populate_lookups.py
```

## URLs

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs (Swagger): http://localhost:8000/docs
- API Docs (ReDoc): http://localhost:8000/redoc
