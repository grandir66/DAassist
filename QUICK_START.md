# 🚀 Quick Start - DAAssist

## Avvio Rapido in 3 Passi

### 1️⃣ Avvia i Container

```bash
./manage.sh start
```

Questo comando avvierà:
- PostgreSQL (porta 5432)
- Redis (porta 6379)
- Backend FastAPI (porta 8000)
- Frontend React (porta 3000)

⏱️ Tempo stimato: ~30 secondi

### 2️⃣ Inizializza il Database

```bash
./manage.sh init
```

Questo comando:
- Crea tutte le tabelle
- Popola le lookup tables
- Crea l'utente admin

⏱️ Tempo stimato: ~5 secondi

### 3️⃣ Accedi all'Applicazione

Apri il browser su: **http://localhost:3000**

**Credenziali:**
- Username: `admin`
- Password: `admin123`

---

## 🎯 Cosa Puoi Fare Subito

### ✅ Testare l'Interfaccia

1. **Login**
   - Accedi con le credenziali admin
   - Prova un login errato per vedere la gestione errori

2. **Dashboard**
   - Visualizza le statistiche (dati mock)
   - Esplora i ticket recenti
   - Visualizza le attività di oggi

3. **Ticket**
   - Lista completa ticket
   - Filtra per priorità/stato (UI pronta, backend TODO)
   - Visualizza badge colorati

4. **Navigazione**
   - Prova tutte le voci del menu
   - Logout e re-login
   - Naviga tra le pagine

### 🔍 Testare l'API

**Swagger UI**: http://localhost:8000/api/docs

**Test Login via cURL:**
```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"

# Risposta:
# {
#   "access_token": "eyJ...",
#   "refresh_token": "eyJ...",
#   "token_type": "bearer"
# }

# Get User Info (sostituisci TOKEN con l'access_token)
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer TOKEN"
```

**Test Lookup Tables:**
```bash
# Get Priorità
curl http://localhost:8000/api/v1/lookup/priorities

# Get Stati Ticket
curl http://localhost:8000/api/v1/lookup/ticket-states

# Get Tipi Intervento
curl http://localhost:8000/api/v1/lookup/intervention-types
```

---

## 📊 Verifica Stato

### Check Containers

```bash
docker-compose ps
```

Dovresti vedere:
```
daassist-postgres   Up (healthy)
daassist-redis      Up (healthy)
daassist-backend    Up
daassist-frontend   Up
```

### Check Logs

```bash
# Backend
./manage.sh logs backend

# Frontend
./manage.sh logs frontend

# Database
./manage.sh logs postgres
```

### Check Database

```bash
# Accedi al database
./manage.sh psql

# Lista tabelle
\dt

# Conta utenti
SELECT COUNT(*) FROM tecnici;

# Exit
\q
```

---

## 🐛 Troubleshooting

### Frontend non si carica

```bash
# Riavvia frontend
docker-compose restart frontend

# Check logs
docker-compose logs -f frontend

# Se necessario, ricompila
docker-compose up -d --build frontend
```

### Backend non risponde

```bash
# Check logs
./manage.sh logs backend

# Riavvia backend
docker-compose restart backend
```

### Database non inizializzato

```bash
# Re-init database
./manage.sh init

# Oppure reset completo
./manage.sh clean
./manage.sh start
./manage.sh init
```

### Porta già in uso

```bash
# Ferma tutto
./manage.sh stop

# Trova processo sulla porta
lsof -i :3000  # o :8000 o :5432

# Riavvia
./manage.sh start
```

---

## 🎨 Cosa Vedere nell'Interfaccia

### 1. Login Page
- ✨ Gradient background (blue → indigo)
- 📝 Form moderno con validazione
- ⚠️ Errori visualizzati con icona e colore
- 🔄 Loading state durante autenticazione
- 💡 Credenziali di default mostrate

### 2. Dashboard
- 📊 4 Card KPI con icone colorate
  - Ticket Aperti (blu)
  - Interventi in Corso (arancione)
  - Completati Oggi (verde)
  - SLA a Rischio (rosso)
- 📋 Lista ticket recenti con badge
- 📅 Timeline attività giornaliere
- 📈 Placeholder grafici performance

### 3. Lista Ticket
- 🔍 Barra ricerca (UI pronta)
- 🎯 Filtri avanzati (UI pronta)
- 📊 Tabella completa con:
  - Numero ticket (link blu)
  - Cliente
  - Oggetto
  - Priorità (badge colorato)
  - Stato (badge colorato)
  - Tecnico assegnato
  - Data creazione
  - Azioni rapide
- ➕ Pulsante "Nuovo Ticket"

### 4. Sidebar Navigation
- 🏠 Dashboard
- 🎫 Ticket
- 🔧 Interventi (placeholder)
- 📅 Calendario (placeholder)
- 👥 Clienti (placeholder)

### 5. User Info
- 👤 Avatar con iniziali
- 📝 Nome completo
- 🏷️ Ruolo utente
- 🚪 Pulsante logout

---

## 🎯 Prossimi Passi

### Per Sviluppatori

1. **Implementare API Tickets**
   ```bash
   cd backend/app/api/v1
   # Creare tickets.py con CRUD completo
   ```

2. **Collegare Dashboard a API reali**
   ```bash
   cd frontend/src/pages
   # Sostituire dati mock in Dashboard.tsx
   ```

3. **Form Nuovo Ticket**
   ```bash
   cd frontend/src/pages
   # Creare NewTicket.tsx con form completo
   ```

4. **Dettaglio Ticket**
   ```bash
   # Creare TicketDetail.tsx con tab
   ```

### Per Tester

1. **Test Autenticazione**
   - Login/Logout
   - Refresh automatico token
   - Redirect se non autenticato

2. **Test Navigazione**
   - Tutte le voci menu
   - Browser back/forward
   - URL diretti

3. **Test UI/UX**
   - Responsive (desktop, TODO mobile)
   - Loading states
   - Errori visualizzati
   - Transizioni smooth

---

## 📖 Documentazione

- **README generale**: `README.md`
- **Setup backend**: `SETUP_COMPLETATO.md`
- **Setup frontend**: `FRONTEND_COMPLETATO.md`
- **Specifiche progetto**: `PROMPT_PROGETTO_COMPLETO.md`

---

## 🎉 Buon Divertimento!

L'applicazione è pronta per essere esplorata e sviluppata ulteriormente.

Per domande o problemi, consulta la documentazione o controlla i log con `./manage.sh logs`.
