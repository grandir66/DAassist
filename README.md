# DAAssist - Sistema Gestione Assistenza IT

Sistema integrato per la gestione dell'assistenza tecnica di una società informatica, che copre l'intero ciclo di vita dalla richiesta del cliente al rapportino di intervento finale.

**Repository**: https://github.com/grandir66/DAassist

## Caratteristiche Principali

- **Gestione Ticket**: Sistema completo di ticketing con SLA tracking
- **Interventi**: Pianificazione ed esecuzione interventi con rapportini
- **Calendario**: Pianificazione operativa con sync Google/Outlook
- **Portale Cliente**: Self-service per apertura ticket e consultazione storico
- **Knowledge Base**: Base di conoscenza interna ed esterna
- **Asset Management**: Inventario infrastruttura cliente con vault credenziali
- **Mobile PWA**: Supporto offline completo per tecnici in campo

## Stack Tecnologico

### Backend
- **Framework**: FastAPI 0.109+
- **Database**: PostgreSQL 15+ (locale) + SQL Server (gestionale)
- **Cache**: Redis
- **ORM**: SQLAlchemy 2.0
- **Auth**: JWT

### Frontend (in sviluppo)
- **Framework**: React 18+
- **State Management**: Zustand
- **UI Components**: Shadcn/ui
- **HTTP Client**: Axios + TanStack Query

## Requisiti

- Docker 20.10+
- Docker Compose 2.0+
- (Opzionale) Python 3.11+ per sviluppo locale
- (Opzionale) Node.js 18+ per frontend

## Quick Start con Docker

### 1. Clona il repository

```bash
git clone <repository-url>
cd DAAssist
```

### 2. Copia il file di configurazione

```bash
cd backend
cp .env.example .env
```

Modifica `.env` con le tue impostazioni (opzionale per sviluppo locale).

### 3. Avvia i container

```bash
# Dalla root del progetto
docker-compose up -d
```

Questo avvierà:
- PostgreSQL su porta 5432
- Redis su porta 6379
- Backend API su porta 8000

### 4. Inizializza il database

```bash
# Entra nel container backend
docker-compose exec backend bash

# Esegui lo script di inizializzazione
python init_db.py

# Esci dal container
exit
```

### 5. Accedi all'applicazione

- **Frontend Web App**: http://localhost:3000
- **API Docs**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **Health Check**: http://localhost:8000/health

**Credenziali di default:**
- Username: `admin`
- Password: `admin123`

⚠️ **IMPORTANTE**: Cambia la password admin in produzione!

### Screenshot

**Login**:
- Interfaccia moderna con gradient background
- Form validato con feedback errori

**Dashboard**:
- Cards con statistiche principali (Ticket aperti, Interventi, SLA)
- Lista ticket recenti
- Attività pianificate per oggi
- Grafici performance (in sviluppo)

**Lista Ticket**:
- Tabella completa con filtri e ricerca
- Badge colorati per priorità e stato
- Azioni rapide su ogni ticket

## Sviluppo Locale (senza Docker)

### Backend

1. **Crea un ambiente virtuale Python**

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# oppure
venv\Scripts\activate  # Windows
```

2. **Installa le dipendenze**

```bash
pip install -r requirements.txt
```

3. **Configura il database**

Assicurati di avere PostgreSQL e Redis in esecuzione localmente, poi:

```bash
cp .env.example .env
# Modifica .env con le tue impostazioni
```

4. **Inizializza il database**

```bash
python init_db.py
```

5. **Avvia il server**

```bash
uvicorn app.main:app --reload --port 8000
```

### Frontend (in sviluppo)

```bash
cd frontend
npm install
npm run dev
```

## Struttura del Progetto

```
DAAssist/
├── backend/
│   ├── app/
│   │   ├── api/v1/          # Endpoint API
│   │   ├── core/            # Config, security, exceptions
│   │   ├── models/          # SQLAlchemy models
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── repositories/    # Data access layer
│   │   ├── services/        # Business logic
│   │   ├── integrations/    # Integrazioni esterne
│   │   └── utils/           # Utilities
│   ├── init_db.py           # Script inizializzazione DB
│   └── requirements.txt
├── frontend/                # React application (TODO)
├── docs/                    # Documentazione
├── docker-compose.yml
└── README.md
```

## API Endpoints

### Autenticazione

- `POST /api/v1/auth/login` - Login
- `GET /api/v1/auth/me` - Informazioni utente corrente
- `POST /api/v1/auth/refresh` - Refresh token

### Lookup Tables

- `GET /api/v1/lookup/channels` - Canali richiesta
- `GET /api/v1/lookup/priorities` - Priorità
- `GET /api/v1/lookup/ticket-states` - Stati ticket
- `GET /api/v1/lookup/intervention-states` - Stati intervento
- `GET /api/v1/lookup/intervention-types` - Tipi intervento
- `GET /api/v1/lookup/activity-categories` - Categorie attività
- `GET /api/v1/lookup/intervention-origins` - Origini intervento
- `GET /api/v1/lookup/departments` - Reparti
- `GET /api/v1/lookup/user-roles` - Ruoli utente

### TODO: Tickets, Interventions, Calendar, etc.

(In fase di sviluppo)

## Testing

```bash
# Backend
cd backend
pytest

# Frontend (quando disponibile)
cd frontend
npm test
```

## Deployment

### Preparazione per produzione

1. **Modifica `.env`**
   - Cambia `DEBUG=False`
   - Imposta `SECRET_KEY` e `JWT_SECRET_KEY` sicuri
   - Configura database produzione
   - Imposta SMTP per email
   - Configura OAuth per calendari esterni

2. **Build dei container**

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml build
```

3. **Avvia in produzione**

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Backup Database

```bash
# Backup
docker-compose exec postgres pg_dump -U daassist daassist > backup_$(date +%Y%m%d).sql

# Restore
docker-compose exec -T postgres psql -U daassist daassist < backup_20241216.sql
```

## Integrazione Gestionale SQL Server

Il sistema sincronizza automaticamente:
- **Import**: Clienti, Contratti, Referenti (ogni 15 minuti)
- **Export**: Rapportini chiusi verso gestionale

Configura la connessione in `.env`:

```env
SQLSERVER_HOST=your-server
SQLSERVER_PORT=1433
SQLSERVER_USER=your-user
SQLSERVER_PASSWORD=your-password
SQLSERVER_DATABASE=your-db
```

## Troubleshooting

### Il backend non si avvia

1. Verifica che PostgreSQL e Redis siano in esecuzione:
   ```bash
   docker-compose ps
   ```

2. Controlla i log:
   ```bash
   docker-compose logs backend
   ```

### Errore di connessione al database

1. Verifica le credenziali in `.env`
2. Assicurati che il database sia stato inizializzato:
   ```bash
   docker-compose exec backend python init_db.py
   ```

### Problemi con le migrazioni

```bash
# Reset completo database (ATTENZIONE: cancella tutti i dati!)
docker-compose down -v
docker-compose up -d
docker-compose exec backend python init_db.py
```

## Contribuire

1. Fork del repository
2. Crea un branch per la feature (`git checkout -b feature/AmazingFeature`)
3. Commit delle modifiche (`git commit -m 'Add some AmazingFeature'`)
4. Push al branch (`git push origin feature/AmazingFeature`)
5. Apri una Pull Request

## Roadmap

### Fase 1: Foundation ✅
- [x] Setup progetto backend
- [x] Schema database
- [x] Sistema autenticazione
- [x] API lookup tables
- [x] Docker setup

### Fase 2: Ticket Management (In corso)
- [ ] CRUD Ticket completo
- [ ] Sistema stati e transizioni
- [ ] Note e messaggi
- [ ] SLA tracking

### Fase 3: Interventi
- [ ] Gestione interventi
- [ ] Righe attività e sessioni
- [ ] Rapportini e firma cliente
- [ ] Export gestionale

### Fase 4-8: Vedi PROMPT_PROGETTO_COMPLETO.md

## Licenza

Proprietario - Tutti i diritti riservati

## Supporto

Per supporto, contatta: support@daassist.local
