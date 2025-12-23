# 🚀 PROMPT COMPLETO: Sistema Gestione Assistenza IT

## Documento per Generazione AI e Sviluppo

**Versione:** 1.0  
**Data:** Dicembre 2024  
**Basato su:** Analisi sistema Stormshield Manager esistente

---

# INDICE

1. [Contesto e Obiettivi](#1-contesto-e-obiettivi)
2. [Analisi Sistema Esistente](#2-analisi-sistema-esistente)
3. [Requisiti Funzionali](#3-requisiti-funzionali)
4. [Architettura Proposta](#4-architettura-proposta)
5. [Modello Dati](#5-modello-dati)
6. [Flussi di Lavoro](#6-flussi-di-lavoro)
7. [API Design](#7-api-design)
8. [Interfaccia Utente](#8-interfaccia-utente)
9. [Integrazioni](#9-integrazioni)
10. [Sicurezza](#10-sicurezza)
11. [Miglioramenti Specifici IT](#11-miglioramenti-specifici-it)
12. [Piano di Sviluppo](#12-piano-di-sviluppo)

---

# 1. CONTESTO E OBIETTIVI

## 1.1 Obiettivo del Progetto

Sviluppare un sistema integrato per la gestione dell'assistenza tecnica di una società informatica, che copra l'intero ciclo di vita dalla richiesta del cliente al rapportino di intervento finale, con sincronizzazione bidirezionale con il gestionale aziendale.

Il sistema deve essere:
- **Autosufficiente**: Funziona in modo autonomo con cache locale dei dati del gestionale
- **Lineare**: Flussi di lavoro chiari senza duplicazioni
- **Integrato**: Sincronizzazione trasparente con gestionale esterno (SQL Server)
- **Mobile-first**: Pieno supporto per operatività in mobilità (PWA offline-first)
- **Tracciabile**: Audit completo di tutte le operazioni

## 1.2 Principi Guida

| Principio | Descrizione |
|-----------|-------------|
| **Autosufficienza** | Cache locale di clienti, contratti, referenti. Il sistema funziona anche se il gestionale è temporaneamente non disponibile |
| **Linearità** | Flussi di lavoro chiari e prevedibili. Evitare duplicazioni di tabelle e funzionalità |
| **Integrazione** | Sincronizzazione periodica con gestionale. Export rapportini chiusi |
| **Mobilità** | PWA con supporto offline completo per tecnici in campo |
| **Tracciabilità** | Audit log completo, storico modifiche, tracking SLA |

## 1.3 Scope

### In Scope
- ✅ Gestione ticket di assistenza (apertura, assegnazione, chiusura)
- ✅ Pianificazione interventi (calendario operativo)
- ✅ Esecuzione e rendicontazione interventi (righe attività, tempi, team)
- ✅ Rapportini e firma cliente (mobile-friendly)
- ✅ Sincronizzazione con gestionale (import clienti, export rapportini)
- ✅ Portale self-service clienti
- ✅ Knowledge base interna
- ✅ Gestione asset cliente (inventario infrastruttura)
- ✅ Tracking SLA automatico
- ✅ App mobile PWA con offline support

### Out of Scope
- ❌ Contabilità e fatturazione completa (delegata a gestionale)
- ❌ CRM completo (solo dati essenziali per assistenza)
- ❌ Gestione magazzino (solo riferimenti a articoli)
- ❌ Gestione progetti complessi (solo progetti semplici)

---

# 2. ANALISI SISTEMA ESISTENTE

## 2.1 Architettura Attuale

Il sistema esistente (Stormshield Manager) è basato su:

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND                                  │
│  Flask Templates (Jinja2) + JavaScript vanilla              │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────┴──────────────────────────────────┐
│                    BACKEND                                   │
│  Python Flask + Blueprints per moduli                       │
│  • auth_middleware.py - Autenticazione JWT                  │
│  • app.py - Entry point e routing principale                │
└──────────────────────────┬──────────────────────────────────┘
                           │
        ┌──────────────────┴──────────────────┐
        │                                      │
┌───────┴───────┐                    ┌────────┴────────┐
│  PostgreSQL   │                    │   SQL Server    │
│   (Locale)    │                    │  (Gestionale)   │
│ • Utenti      │                    │ • Clienti       │
│ • Config      │                    │ • Contratti     │
│ • Richieste   │                    │ • Interventi    │
└───────────────┘                    └─────────────────┘
```

## 2.2 Moduli Esistenti Analizzati

### 2.2.1 Tickets Manager

**Percorso:** `modules/tickets_manager/`

**Database (`tickets_database.py`):**
- Connessione a SQL Server (preferenza replica `domarc_replica`)
- Tabelle principali: `girichieste_domarc`, `gistatirichieste`
- Funzioni principali:
  - `search_tickets()` - Ricerca con filtri multipli
  - `get_ticket_detail()` - Dettaglio completo ticket
  - `create_ticket()` - Creazione nuovo ticket
  - `update_ticket_field()` - Aggiornamento campi
  - `assign_ticket_to_operator()` - Assegnazione tecnico
  - `close_ticket()` - Chiusura con opzioni (diretta, intervento, schedulazione)
  - `reopen_ticket()` - Riapertura ticket chiuso

**Routes (`tickets_routes.py`):**
- `/tickets/` - Lista ticket (pagina principale)
- `/tickets/new` - Creazione nuovo ticket
- `/tickets/detail/<tk_key>` - Dettaglio ticket
- API REST per operazioni CRUD

**Criticità identificate:**
- Logica mista tra locale e gestionale
- Stati non sempre coerenti
- Mancanza di SLA strutturato
- Note e messaggi non separati chiaramente

### 2.2.2 Interventions Manager

**Percorso:** `modules/interventions/`

**Database (`interventions_database.py`):**
- Lettura da `giinterventih` (header intervento)
- Righe attività: `giinterventir`
- Tempi: `giinterventit`, `tbint_time` (tabella temporanea)
- Tecnici aggiuntivi: `giinterventirt`

**Funzioni principali:**
- `search_interventions()` - Ricerca interventi con filtri
- `get_intervention_detail()` - Dettaglio completo con righe, tempi, tecnici

**Criticità identificate:**
- Struttura complessa ereditata dal gestionale
- Difficoltà nel tracciare interventi multi-giorno
- Mancanza di firma digitale integrata
- Numerazione serie complessa

### 2.2.3 Calendar

**Percorso:** `modules/calendar/`

**Database (`calendar_database.py`):**
- Eventi in `gicalendario`
- Colori da `CalendarColorManager`
- Tipologie lavoro da `gilavori`, `giicons`

**Requests Database (`requests_database.py`):**
- Richieste intervento in PostgreSQL locale
- Stati: pendente, pianificata, completata
- Funzione `assign_to_calendar()` crea evento in SQL Server

**Criticità identificate:**
- Doppia gestione (locale + gestionale)
- Mancanza sync calendari esterni
- UI non ottimizzata per drag & drop
- Colori hardcoded

### 2.2.4 Rapportini

**Percorso:** `modules/rapportini/`

**Database (`rapportini_database.py`):**
- Creazione interventi completi
- Gestione numerazione serie
- Chiusura e sincronizzazione

**Funzioni principali:**
- `create_rapportino()` - Creazione completo intervento
- `close_rapportino()` - Chiusura e export
- `get_next_intervention_number()` - Numerazione

**Criticità identificate:**
- Logica complessa per numerazione
- Tabelle temporanee (`tbint_time`)
- Mancanza firma cliente mobile
- Export gestionale non robusto

## 2.3 Punti di Forza da Mantenere

1. ✅ **Autenticazione robusta** - JWT + LDAP + locale funziona bene
2. ✅ **Struttura modulare** - Blueprint Flask ben organizzati
3. ✅ **Integrazione gestionale** - Pattern di connessione consolidato
4. ✅ **Calendario funzionale** - Vista calendario operativa

## 2.4 Aree di Miglioramento

1. 🔴 **Unificazione database** - Troppa frammentazione tra PostgreSQL e SQL Server
2. 🔴 **API consistente** - Standardizzare REST API
3. 🔴 **Mobile** - Da template HTML a PWA vera
4. 🟡 **UX** - Modernizzare interfaccia utente
5. 🟡 **Automazioni** - SLA, escalation, notifiche mancanti

---

# 3. REQUISITI FUNZIONALI

## 3.1 Gestione Ticket

### RF-TK-01: Creazione Ticket

**Campi obbligatori:**
- Cliente (da anagrafica gestionale)
- Canale richiesta (Telefono, Email, WebApp, Voce, Portale)
- Oggetto (max 200 caratteri)
- Priorità (default: Normale)

**Campi opzionali:**
- Referente (selezionabile o testo libero)
- Descrizione (testo libero)
- Contratto (suggerito se cliente ha contratti attivi)
- Asset collegato

**Validazioni:**
- Cliente deve esistere in cache locale
- Se contratto specificato, deve essere attivo
- Oggetto non vuoto

### RF-TK-02: Stati Ticket

```
NUOVO 
  ↓ (presa in carico)
PRESO_CARICO 
  ↓ (inizio lavorazione)
IN_LAVORAZIONE 
  ├─→ SCHEDULATO (se richiede pianificazione)
  └─→ CHIUSO (risolto)
      ├─ Diretta (senza intervento)
      ├─ Con intervento immediato
      └─ Con richiesta intervento
```

**Transizioni valide:**
- NUOVO → PRESO_CARICO (solo tecnico)
- PRESO_CARICO → IN_LAVORAZIONE (solo tecnico assegnato)
- IN_LAVORAZIONE → SCHEDULATO (genera richiesta intervento)
- IN_LAVORAZIONE → CHIUSO (risoluzione diretta)
- SCHEDULATO → CHIUSO (dopo intervento completato)
- Qualsiasi → ANNULLATO (con motivo)

### RF-TK-03: Opzioni Chiusura Ticket

| Tipo Chiusura | Descrizione | Azione Successiva |
|---------------|-------------|-------------------|
| **Diretta** | Risolto senza intervento | Solo note chiusura, stato CHIUSO |
| **Con intervento immediato** | Risolto con intervento stesso giorno | Crea intervento, chiude ticket |
| **Con richiesta intervento** | Necessita pianificazione | Crea richiesta intervento, stato SCHEDULATO |

### RF-TK-04: Funzionalità Aggiuntive

- **Note interne**: Non visibili a cliente, per comunicazione tecnici
- **Messaggi cliente**: Visibili su portale, comunicazione bidirezionale
- **Allegati**: File, screenshot, documenti
- **Link a KB**: Collegamento a articoli knowledge base risolutivi
- **Storico completo**: Log di tutte le modifiche con timestamp e utente

## 3.2 Gestione Interventi

### RF-IN-01: Origini Intervento

| Origine | Descrizione | Quando si usa |
|---------|-------------|---------------|
| **Da Ticket** | Generato da chiusura ticket | Ticket chiuso con richiesta intervento |
| **Da Pianificazione** | Schedulato da calendario | Richiesta intervento pianificata |
| **Da Progetto** | Parte di progetto cliente | Intervento collegato a progetto |
| **Spontaneo** | Inserito direttamente | Tecnico crea intervento manualmente |
| **Da Contratto** | Manutenzione programmata | Attività ricorrente da contratto |

### RF-IN-02: Tipi Intervento

| Tipo | Descrizione | Colore Calendario | Richiede Viaggio |
|------|-------------|-------------------|------------------|
| **Presso cliente** | Intervento on-site | 🔵 Blu (#3B82F6) | Sì |
| **In laboratorio** | Lavoro in sede | 🟢 Verde (#10B981) | No |
| **Remoto** | Assistenza remota | 🟡 Giallo (#F59E0B) | No |
| **Telefonico** | Solo supporto telefonico | 🟠 Arancione (#8B5CF6) | No |

### RF-IN-03: Categorie Attività

- **Tecnica** (hardware, riparazioni) - €50/ora
- **Sistemistica** (server, reti, backup) - €60/ora
- **Gestionale** (software gestionali) - €55/ora
- **Centralino** (VoIP, telefonia) - €50/ora
- **Security** (firewall, antivirus, cyber) - €70/ora
- **Consulenza** (analisi, formazione) - €80/ora
- **Sviluppo** (software custom) - €75/ora
- **Formazione** - €60/ora
- **Altro** (da specificare)

### RF-IN-04: Struttura Intervento

```
INTERVENTO (Header)
├── Informazioni base
│   ├── Numero progressivo
│   ├── Cliente
│   ├── Tecnico principale
│   ├── Tipo intervento
│   ├── Stato
│   └── Date inizio/fine
│
├── RIGHE ATTIVITÀ (N)
│   ├── Categoria attività
│   ├── Descrizione lavoro
│   ├── Quantità / Unità misura
│   ├── Prezzo unitario
│   ├── Sconto %
│   ├── Flag: fatturabile, garanzia, contratto
│   └── Link a sessione lavoro (opzionale)
│
├── SESSIONI LAVORO (N)
│   ├── Data
│   ├── Ora inizio/fine
│   ├── Durata (calcolata o manuale)
│   ├── Tecnico
│   ├── Tipo intervento (remoto, cliente, etc.)
│   ├── Km percorsi
│   ├── Tempo viaggio
│   └── Geolocalizzazione (opzionale)
│
├── TECNICI TEAM (N)
│   ├── Tecnico
│   ├── Ruolo (principale, supporto, formazione)
│   ├── Ore lavorate
│   └── Note
│
└── ALLEGATI (N)
    ├── Foto
    ├── Documenti
    ├── Screenshot
    └── Firma cliente (base64)
```

**Note importanti:**
- Un intervento può avere più righe attività
- Ogni riga può essere associata a una sessione lavoro
- Un intervento può durare più giorni (una sessione per giorno)
- Le righe possono essere aggiunte anche dopo la chiusura (per correzioni)

### RF-IN-05: Stati Intervento

```
BOZZA 
  ↓ (pianificazione)
PIANIFICATO 
  ↓ (inizio lavorazione)
IN_CORSO 
  ↓ (completamento attività)
COMPLETATO 
  ↓ (firma cliente + chiusura)
CHIUSO 
  ↓ (export gestionale)
SINCRONIZZATO
```

**Transizioni valide:**
- BOZZA → PIANIFICATO (assegnato a calendario)
- PIANIFICATO → IN_CORSO (inizio lavorazione)
- IN_CORSO → COMPLETATO (attività completate)
- COMPLETATO → CHIUSO (firma cliente raccolta)
- CHIUSO → SINCRONIZZATO (export gestionale riuscito)

### RF-IN-06: Chiusura e Rapportino

**Workflow chiusura:**

1. **Tecnico completa attività**
   - Aggiunge tutte le righe attività
   - Registra tutte le sessioni lavoro
   - Compila note finali

2. **Raccoglie firma cliente**
   - Canvas touch su mobile
   - Nome e ruolo firmatario
   - Data/ora firma
   - Salvataggio base64

3. **Sistema genera rapportino**
   - Calcolo totale ore
   - Calcolo totale costi
   - Generazione PDF (opzionale)

4. **Rapportino esportato a gestionale**
   - Inserimento in tabelle `giinterventih`, `giinterventir`, `giinterventit`
   - Numerazione serie gestionale
   - Gestione errori e retry

5. **Stato → SINCRONIZZATO**
   - Flag `sincronizzato_gestionale = TRUE`
   - Timestamp sincronizzazione
   - Codice gestionale salvato

## 3.3 Calendario

### RF-CA-01: Viste Calendario

- **Giornaliera**: Timeline oraria (08:00 - 20:00)
- **Settimanale**: Colonne per giorno, righe per tecnico (opzionale)
- **Mensile**: Griglia con eventi compatti
- **Agenda**: Lista eventi ordinata per data/ora

### RF-CA-02: Gestione Eventi

- **Creazione**: Drag & drop su slot vuoto
- **Spostamento**: Trascinamento evento su nuovo slot
- **Ridimensionamento**: Modifica durata trascinando bordi
- **Assegnazione multipla**: Più tecnici per evento
- **Colori**: Per tipo intervento, stato, tecnico (configurabile)

### RF-CA-03: Filtri

- Per tecnico (singolo o multiplo)
- Per reparto
- Per tipo intervento
- Per stato
- Per cliente
- Combinazione filtri (AND)

### RF-CA-04: Sincronizzazione Esterna

- **Google Calendar**: OAuth2, sync bidirezionale
- **Microsoft 365 / Outlook**: OAuth2, sync bidirezionale
- **CalDAV generico**: Per altri client calendario
- **Conflict resolution**: Precedenza sistema locale

## 3.4 Portale Cliente

### RF-PC-01: Funzionalità Cliente

- **Login dedicato**: Email + password (separato da tecnici)
- **Apertura nuovo ticket**: Form semplificato
- **Visualizzazione ticket**: Propri ticket o tutti ticket azienda (configurabile)
- **Messaggistica**: Chat con tecnico assegnato
- **Consultazione storico**: Interventi passati
- **Download rapportini**: PDF rapportini chiusi
- **Accesso KB**: Knowledge base pubblica

### RF-PC-02: Notifiche Cliente

- Email su apertura ticket
- Email su aggiornamenti ticket
- Email su chiusura ticket
- Riepilogo periodico (settimanale/mensile, configurabile)

## 3.5 Knowledge Base

### RF-KB-01: Articoli

- Titolo, contenuto rich-text (Markdown o HTML)
- Categorie gerarchiche
- Tag per ricerca
- Link a prodotti/servizi
- Visibilità: interna (solo tecnici) o pubblica (anche clienti)

### RF-KB-02: Utilizzo

- Ricerca full-text su titolo e contenuto
- Suggerimenti durante risoluzione ticket
- Tracking articoli più utili
- Collegamento ticket → articolo risolutivo

## 3.6 Asset Management

### RF-AM-01: Inventario

**Tipi asset:**
- Server (fisico, virtuale)
- PC/Workstation
- Firewall
- Switch/Router
- NAS/Storage
- Stampante/Scanner
- Telefono/VoIP
- Altro

**Dati asset:**
- Hostname, IP, MAC
- Serial number, asset tag
- Sistema operativo, versione
- Specifiche hardware (JSON)
- Licenze software (JSON)
- Stato: Attivo, Dismissione, Guasto, Sostituito
- Ubicazione fisica

### RF-AM-02: Credenziali

- Vault criptato (AES-256)
- Accesso loggato (chi, quando, perché)
- Collegamento a asset
- Rotazione password suggerita
- Scadenza password

### RF-AM-03: Storico

- Log modifiche configurazione
- Collegamento a interventi
- Timeline asset completa

## 3.7 SLA Management

### RF-SLA-01: Definizione SLA

**Parametri configurabili:**
- Tempi risposta per priorità (ore lavorative)
- Tempi risoluzione per priorità (ore lavorative)
- Finestre orarie lavorative (es. 08:00-18:00)
- Giorni lavorativi (es. Lun-Ven)
- Include festivi: Sì/No

**Esempio SLA Standard:**
- Critica: Risposta 1h, Risoluzione 4h
- Urgente: Risposta 2h, Risoluzione 8h
- Alta: Risposta 4h, Risoluzione 16h
- Normale: Risposta 8h, Risoluzione 24h
- Bassa: Risposta 24h, Risoluzione 72h

### RF-SLA-02: Tracking

- Calcolo automatico scadenze al creare ticket
- Pause per attesa cliente (SLA fermato)
- Alert pre-scadenza (es. 1 ora prima)
- Report compliance mensile

## 3.8 Mobile PWA

### RF-MW-01: Offline

- Cache interventi assegnati al tecnico
- Operazioni in coda offline
- Sync automatico quando online
- Indicatore stato connessione

### RF-MW-02: Funzionalità

- **Lista interventi**: Giornalieri assegnati al tecnico
- **Dettaglio intervento**: Con tutte le informazioni
- **Aggiungi righe/tempi**: Form semplificati
- **Firma cliente**: Canvas touch, salvataggio base64
- **Foto**: Accesso camera, compressione automatica
- **Geolocalizzazione**: Opzionale, per check-in/out
- **Timer lavoro**: Avvio/stop sessione con un tap

---

# 4. ARCHITETTURA PROPOSTA

## 4.1 Stack Tecnologico Consigliato

### Backend

**Opzione 1: Python/FastAPI** (Consigliata)
- Framework: FastAPI 0.104+
- ORM: SQLAlchemy 2.0
- Validation: Pydantic v2
- Auth: python-jose (JWT)
- Task Queue: Celery + Redis
- WebSocket: FastAPI WebSocket

**Opzione 2: Node.js/NestJS**
- Framework: NestJS 10+
- ORM: TypeORM o Prisma
- Validation: class-validator
- Auth: @nestjs/jwt
- Task Queue: Bull + Redis
- WebSocket: Socket.io

### Frontend

**Opzione 1: React** (Consigliata)
- Framework: React 18+
- State: Zustand o Redux Toolkit
- UI Components: Shadcn/ui o Material-UI
- Calendar: FullCalendar
- Forms: React Hook Form
- HTTP: Axios + TanStack Query

**Opzione 2: Vue.js**
- Framework: Vue 3 Composition API
- State: Pinia
- UI Components: Vuetify 3
- Calendar: FullCalendar
- Forms: VeeValidate
- HTTP: Axios + Vue Query

### Mobile PWA

- Framework: Stesso del web (React/Vue)
- Offline Storage: IndexedDB (Dexie.js)
- Service Worker: Workbox
- Push: Web Push API

### Database

- **PostgreSQL 15+**: Database principale locale
- **Redis**: Cache, sessioni, code
- **SQL Server**: Gestionale (read + write rapportini)

### Infrastructure

- Container: Docker + Docker Compose
- Reverse Proxy: Nginx o Traefik
- CI/CD: GitHub Actions o GitLab CI
- Monitoring: Prometheus + Grafana

## 4.2 Architettura Applicativa

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                 CLIENTS                                          │
├─────────────────┬─────────────────┬─────────────────┬───────────────────────────┤
│   Web Desktop   │    PWA Mobile   │ Portale Cliente │      API Esterne          │
│   (React/Vue)   │  (Offline-first)│   (React/Vue)   │    (Monitoring, etc.)     │
└────────┬────────┴────────┬────────┴────────┬────────┴────────────┬──────────────┘
         │                 │                 │                     │
         └─────────────────┴────────┬────────┴─────────────────────┘
                                    │
                              HTTPS/WSS
                                    │
┌───────────────────────────────────┴─────────────────────────────────────────────┐
│                              API GATEWAY                                         │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐               │
│  │    Auth     │ │    Rate     │ │   CORS      │ │   Logging   │               │
│  │   (JWT)     │ │   Limiting  │ │   Handler   │ │   Request   │               │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘               │
└───────────────────────────────────┬─────────────────────────────────────────────┘
                                    │
┌───────────────────────────────────┴─────────────────────────────────────────────┐
│                           APPLICATION LAYER                                      │
│                                                                                  │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐           │
│  │   Ticket     │ │  Intervento  │ │  Calendario  │ │   Cliente    │           │
│  │   Service    │ │   Service    │ │   Service    │ │   Service    │           │
│  └──────┬───────┘ └──────┬───────┘ └──────┬───────┘ └──────┬───────┘           │
│         │                │                │                │                    │
│  ┌──────┴────────────────┴────────────────┴────────────────┴───────┐           │
│  │                      DOMAIN SERVICES                             │           │
│  │  • SLA Calculator    • Notification Engine    • Sync Manager    │           │
│  │  • Escalation Engine • Report Generator       • Search Engine   │           │
│  └──────────────────────────────┬───────────────────────────────────┘           │
│                                 │                                               │
│  ┌──────────────────────────────┴───────────────────────────────────┐           │
│  │                    DATA ACCESS LAYER                              │           │
│  │         Repository Pattern + Unit of Work                        │           │
│  └──────────────────────────────┬───────────────────────────────────┘           │
│                                 │                                               │
└─────────────────────────────────┼───────────────────────────────────────────────┘
                                  │
         ┌────────────────────────┴────────────────────────┐
         │                                                 │
┌────────┴────────┐                              ┌─────────┴─────────┐
│   PostgreSQL    │                              │    SQL Server     │
│    (Locale)    │                              │   (Gestionale)    │
│                 │                              │                   │
│ • Ticket        │         SYNC                 │ • Clienti         │
│ • Interventi    │ ◄─────────────────────────►  │ • Contratti       │
│ • Calendario    │                              │ • Rapportini      │
│ • KB            │                              │ • (export only)   │
│ • Asset         │                              │                   │
│ • Utenti        │                              │                   │
│ • Config        │                              │                   │
│ • Cache         │                              │                   │
└─────────────────┘                              └───────────────────┘
```

## 4.3 Struttura Progetto (Python/FastAPI)

```
assistenza-it/
├── docker-compose.yml
├── docker-compose.dev.yml
├── .env.example
├── README.md
│
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── alembic.ini
│   ├── alembic/
│   │   └── versions/
│   │
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # Entry point FastAPI
│   │   ├── config.py               # Configurazione
│   │   ├── dependencies.py        # Dependency injection
│   │   │
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── v1/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── router.py       # Router principale v1
│   │   │   │   ├── tickets.py
│   │   │   │   ├── interventions.py
│   │   │   │   ├── calendar.py
│   │   │   │   ├── clients.py
│   │   │   │   ├── assets.py
│   │   │   │   ├── kb.py
│   │   │   │   ├── auth.py
│   │   │   │   └── sync.py
│   │   │   └── deps.py             # Dependencies API
│   │   │
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── security.py         # JWT, hashing
│   │   │   ├── config.py           # Settings
│   │   │   └── exceptions.py      # Custom exceptions
│   │   │
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── base.py             # Base model
│   │   │   ├── ticket.py
│   │   │   ├── intervention.py
│   │   │   ├── calendar.py
│   │   │   ├── client.py
│   │   │   ├── asset.py
│   │   │   ├── kb.py
│   │   │   ├── user.py
│   │   │   └── lookup.py
│   │   │
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── ticket.py           # Pydantic schemas
│   │   │   ├── intervention.py
│   │   │   ├── calendar.py
│   │   │   └── ...
│   │   │
│   │   ├── repositories/
│   │   │   ├── __init__.py
│   │   │   ├── base.py             # Base repository
│   │   │   ├── ticket.py
│   │   │   ├── intervention.py
│   │   │   └── ...
│   │   │
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── ticket.py           # Business logic
│   │   │   ├── intervention.py
│   │   │   ├── calendar.py
│   │   │   ├── sla.py              # SLA calculation
│   │   │   ├── notification.py     # Notifiche
│   │   │   ├── escalation.py       # Escalation rules
│   │   │   ├── sync.py             # Sync gestionale
│   │   │   └── report.py           # Generazione report
│   │   │
│   │   ├── integrations/
│   │   │   ├── __init__.py
│   │   │   ├── gestionale.py       # Connessione SQL Server
│   │   │   ├── google_calendar.py
│   │   │   ├── microsoft365.py
│   │   │   └── email.py
│   │   │
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── pagination.py
│   │       ├── filtering.py
│   │       └── helpers.py
│   │
│   └── tests/
│       ├── __init__.py
│       ├── conftest.py
│       ├── test_tickets.py
│       └── ...
│
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   │
│   ├── public/
│   │   ├── manifest.json           # PWA manifest
│   │   └── sw.js                   # Service worker
│   │
│   └── src/
│       ├── main.tsx
│       ├── App.tsx
│       ├── router.tsx
│       │
│       ├── api/
│       │   ├── client.ts           # Axios instance
│       │   ├── tickets.ts
│       │   ├── interventions.ts
│       │   └── ...
│       │
│       ├── components/
│       │   ├── ui/                 # Componenti base
│       │   ├── tickets/
│       │   ├── interventions/
│       │   ├── calendar/
│       │   └── ...
│       │
│       ├── pages/
│       │   ├── Dashboard.tsx
│       │   ├── tickets/
│       │   ├── interventions/
│       │   ├── calendar/
│       │   └── ...
│       │
│       ├── stores/
│       │   ├── auth.ts
│       │   ├── tickets.ts
│       │   └── ...
│       │
│       ├── hooks/
│       │   ├── useTickets.ts
│       │   ├── useOffline.ts
│       │   └── ...
│       │
│       ├── utils/
│       │   ├── date.ts
│       │   ├── format.ts
│       │   └── ...
│       │
│       └── types/
│           ├── ticket.ts
│           ├── intervention.ts
│           └── ...
│
├── portal/                         # Portale cliente (separato)
│   └── ...
│
└── docs/
    ├── api/
    │   └── openapi.yaml
    ├── database/
    │   └── schema.sql
    └── guides/
        ├── deployment.md
        └── development.md
```

---

# 5. MODELLO DATI

## 5.1 Principi di Design

1. **Normalizzazione**: Evitare duplicazioni, mantenere integrità referenziale
2. **Cache gestionale**: Tabelle `cache_*` per dati sincronizzati
3. **Audit completo**: Log di tutte le modifiche
4. **Soft delete**: Flag `attivo` invece di DELETE fisico
5. **Timestamps**: `created_at`, `updated_at` su tutte le tabelle

## 5.2 Entità Principali

### 5.2.1 Ticket

**Tabella:** `ticket`

**Campi principali:**
- `id` (PK)
- `numero` (UNIQUE, generato automaticamente)
- `cliente_id` (FK → cache_clienti)
- `referente_id` (FK → cache_referenti, nullable)
- `canale_id` (FK → lookup_canali_richiesta)
- `oggetto`, `descrizione`
- `priorita_id` (FK → lookup_priorita)
- `stato_id` (FK → lookup_stati_ticket)
- `tecnico_assegnato_id` (FK → tecnici)
- `contratto_id` (FK → cache_contratti)
- `data_chiusura`, `tipo_chiusura`, `note_chiusura`
- `created_at`, `updated_at`

**Tabelle correlate:**
- `ticket_note` - Note interne
- `ticket_messaggi` - Messaggi cliente-tecnico
- `ticket_allegati` - File allegati
- `ticket_sla_tracking` - Tracking SLA
- `ticket_kb_solutions` - Link a KB

### 5.2.2 Intervento

**Tabella:** `interventi`

**Campi principali:**
- `id` (PK)
- `numero` (UNIQUE, generato automaticamente)
- `serie` (per numerazione gestionale)
- `origine_id` (FK → lookup_origini_intervento)
- `ticket_id` (FK → ticket, nullable)
- `richiesta_id` (FK → richieste_intervento, nullable)
- `evento_calendario_id` (FK → calendario_eventi, nullable)
- `cliente_id` (FK → cache_clienti)
- `tipo_intervento_id` (FK → lookup_tipi_intervento)
- `stato_id` (FK → lookup_stati_intervento)
- `tecnico_id` (FK → tecnici)
- `oggetto`, `descrizione_lavoro`, `note_interne`
- `data_inizio`, `data_fine`
- `firma_cliente` (TEXT, base64)
- `sincronizzato_gestionale`, `codice_gestionale`
- `created_at`, `updated_at`

**Tabelle correlate:**
- `interventi_righe` - Righe attività
- `interventi_sessioni` - Sessioni lavoro (tempi)
- `interventi_tecnici` - Team tecnici
- `interventi_allegati` - Foto, documenti, firma

### 5.2.3 Calendario

**Tabella:** `calendario_eventi`

**Campi principali:**
- `id` (PK)
- `data_inizio`, `data_fine` (TIMESTAMP WITH TIME ZONE)
- `titolo`, `descrizione`, `luogo`
- `tipo_intervento_id` (FK → lookup_tipi_intervento)
- `cliente_id` (FK → cache_clienti)
- `richiesta_id` (FK → richieste_intervento)
- `intervento_id` (FK → interventi)
- `tecnico_principale_id` (FK → tecnici)
- `stato` (PIANIFICATO, CONFERMATO, IN_CORSO, COMPLETATO)
- `google_event_id`, `outlook_event_id` (per sync)
- `colore` (override colore default)
- `created_at`, `updated_at`

**Tabelle correlata:**
- `calendario_tecnici` - Assegnazione multipla tecnici

### 5.2.4 Cache Gestionale

**Tabelle:**
- `cache_clienti` - Anagrafica clienti sincronizzata
- `cache_contratti` - Contratti attivi
- `cache_referenti` - Referenti clienti

**Campi comuni:**
- `codice_gestionale` (UNIQUE, chiave esterna)
- `ultimo_sync` (TIMESTAMP)
- `attivo` (BOOLEAN)

## 5.3 Schema SQL Completo

Vedi file separato `SCHEMA_DATABASE_COMPLETO.sql` per lo schema completo con:
- Tutte le tabelle CREATE TABLE
- Indici per performance
- Foreign keys
- Trigger per numerazione automatica
- Viste materializzate per KPI
- Funzioni PL/pgSQL

**Punti chiave schema:**
- Tutte le tabelle hanno `created_at` e `updated_at`
- Soft delete con flag `attivo`
- Numerazione automatica con sequence
- Indici su campi frequentemente filtrati
- Full-text search su campi testuali (pg_trgm)

---

# 6. FLUSSI DI LAVORO

## 6.1 Flusso Ticket Completo

```
1. APERTURA TICKET
   ├─ Cliente chiama / apre portale
   ├─ Operatore crea ticket
   ├─ Sistema assegna numero progressivo
   ├─ Sistema calcola SLA (se contratto ha SLA)
   └─ Stato: NUOVO

2. ASSEGNAZIONE
   ├─ Tecnico prende in carico
   ├─ Sistema aggiorna stato: PRESO_CARICO
   ├─ Sistema registra prima risposta (SLA)
   └─ Notifica tecnico assegnato

3. LAVORAZIONE
   ├─ Tecnico inizia lavorazione
   ├─ Sistema aggiorna stato: IN_LAVORAZIONE
   ├─ Tecnico aggiunge note/messaggi
   └─ Sistema verifica SLA (alert se prossimo scadenza)

4. CHIUSURA
   ├─ Opzione A: Chiusura diretta
   │  ├─ Tecnico chiude con note
   │  ├─ Sistema aggiorna stato: CHIUSO
   │  ├─ Sistema verifica SLA (risoluzione)
   │  └─ Notifica cliente
   │
   ├─ Opzione B: Intervento immediato
   │  ├─ Tecnico crea intervento
   │  ├─ Sistema collega ticket → intervento
   │  ├─ Intervento completato
   │  ├─ Ticket chiuso automaticamente
   │  └─ Notifica cliente
   │
   └─ Opzione C: Richiesta intervento
      ├─ Sistema crea richiesta_intervento
      ├─ Sistema aggiorna stato: SCHEDULATO
      ├─ Richiesta pianificata su calendario
      ├─ Evento calendario → Intervento
      ├─ Intervento completato
      ├─ Ticket chiuso automaticamente
      └─ Notifica cliente
```

## 6.2 Flusso Intervento Completo

```
1. CREAZIONE
   ├─ Origine: Ticket / Pianificazione / Progetto / Spontaneo
   ├─ Sistema assegna numero progressivo
   ├─ Sistema imposta stato: BOZZA o PIANIFICATO
   └─ Assegnazione tecnico principale

2. PIANIFICAZIONE (se necessario)
   ├─ Creazione evento calendario
   ├─ Assegnazione tecnici team
   ├─ Notifica tecnici assegnati
   └─ Sync calendario esterno (se configurato)

3. ESECUZIONE
   ├─ Tecnico avvia intervento
   ├─ Sistema aggiorna stato: IN_CORSO
   ├─ Tecnico aggiunge righe attività
   ├─ Tecnico registra sessioni lavoro
   ├─ Tecnico aggiunge tecnici team (se necessario)
   ├─ Tecnico scatta foto / aggiunge allegati
   └─ Sistema traccia ore lavorate

4. COMPLETAMENTO
   ├─ Tecnico completa tutte le attività
   ├─ Sistema aggiorna stato: COMPLETATO
   ├─ Sistema genera preview rapportino
   └─ Pronto per firma cliente

5. FIRMA CLIENTE
   ├─ Tecnico mostra rapportino su mobile
   ├─ Cliente firma su canvas touch
   ├─ Sistema salva firma (base64)
   ├─ Sistema registra nome/ruolo firmatario
   └─ Sistema aggiorna stato: CHIUSO

6. SINCRONIZZAZIONE GESTIONALE
   ├─ Sistema genera rapportino completo
   ├─ Sistema esporta a SQL Server
   │  ├─ Inserimento giinterventih
   │  ├─ Inserimento giinterventir (righe)
   │  ├─ Inserimento giinterventit (tempi)
   │  └─ Inserimento giinterventirt (tecnici)
   ├─ Sistema ottiene codice gestionale
   ├─ Sistema aggiorna stato: SINCRONIZZATO
   └─ Sistema logga sync (sync_log)
```

## 6.3 Flusso Sincronizzazione Gestionale

```
SYNC IMPORT (Clienti/Contratti/Referenti)
├─ Scheduler attivato ogni X minuti
├─ Query SQL Server per nuovi/modificati
├─ Confronto con cache locale
├─ Inserimento/aggiornamento cache
├─ Aggiornamento ultimo_sync
└─ Log operazione (sync_log)

SYNC EXPORT (Rapportini)
├─ Query interventi chiusi non sincronizzati
├─ Per ogni intervento:
│  ├─ Generazione dati formato gestionale
│  ├─ Inserimento in SQL Server
│  ├─ Gestione errori (retry se necessario)
│  ├─ Aggiornamento flag sincronizzato
│  └─ Log operazione
└─ Notifica errori persistenti
```

---

# 7. API DESIGN

## 7.1 Principi REST

- **Versioning**: `/api/v1/`
- **Autenticazione**: JWT Bearer token
- **Pagination**: `?page=1&limit=20`
- **Filtering**: `?stato=CHIUSO&cliente_id=123`
- **Sorting**: `?sort=created_at&order=desc`
- **Errori**: RFC 7807 Problem Details

## 7.2 Endpoints Principali

### 7.2.1 Ticket

```
GET    /api/v1/tickets                    # Lista ticket (con filtri)
POST   /api/v1/tickets                    # Crea ticket
GET    /api/v1/tickets/:id                 # Dettaglio ticket
PATCH  /api/v1/tickets/:id                # Aggiorna ticket
DELETE /api/v1/tickets/:id                # Annulla ticket

POST   /api/v1/tickets/:id/take           # Prendi in carico
POST   /api/v1/tickets/:id/assign         # Assegna a tecnico
POST   /api/v1/tickets/:id/close          # Chiudi ticket
POST   /api/v1/tickets/:id/reopen         # Riapri ticket
POST   /api/v1/tickets/:id/intervention   # Genera intervento

GET    /api/v1/tickets/:id/notes           # Note ticket
POST   /api/v1/tickets/:id/notes          # Aggiungi nota
GET    /api/v1/tickets/:id/messages       # Messaggi ticket
POST   /api/v1/tickets/:id/messages       # Invia messaggio
GET    /api/v1/tickets/:id/attachments    # Allegati
POST   /api/v1/tickets/:id/attachments    # Carica allegato
```

### 7.2.2 Interventi

```
GET    /api/v1/interventions               # Lista interventi
POST   /api/v1/interventions               # Crea intervento
GET    /api/v1/interventions/:id          # Dettaglio intervento
PATCH  /api/v1/interventions/:id          # Aggiorna intervento

GET    /api/v1/interventions/:id/rows     # Righe attività
POST   /api/v1/interventions/:id/rows     # Aggiungi riga
PATCH  /api/v1/interventions/:id/rows/:rowId
DELETE /api/v1/interventions/:id/rows/:rowId

GET    /api/v1/interventions/:id/sessions # Sessioni lavoro
POST   /api/v1/interventions/:id/sessions # Aggiungi sessione
PATCH  /api/v1/interventions/:id/sessions/:sessionId
DELETE /api/v1/interventions/:id/sessions/:sessionId

GET    /api/v1/interventions/:id/technicians
POST   /api/v1/interventions/:id/technicians
DELETE /api/v1/interventions/:id/technicians/:techId

POST   /api/v1/interventions/:id/sign     # Firma cliente
POST   /api/v1/interventions/:id/close    # Chiudi intervento
POST   /api/v1/interventions/:id/sync     # Sincronizza gestionale
```

### 7.2.3 Calendario

```
GET    /api/v1/calendar/events            # Eventi (range date)
POST   /api/v1/calendar/events             # Crea evento
GET    /api/v1/calendar/events/:id         # Dettaglio evento
PATCH  /api/v1/calendar/events/:id        # Modifica evento
DELETE /api/v1/calendar/events/:id         # Elimina evento

POST   /api/v1/calendar/events/:id/start  # Avvia intervento
POST   /api/v1/calendar/events/:id/technicians
DELETE /api/v1/calendar/events/:id/technicians/:techId

GET    /api/v1/calendar/sync/google        # Sync Google Calendar
POST   /api/v1/calendar/sync/google/authorize
GET    /api/v1/calendar/sync/outlook       # Sync Outlook
POST   /api/v1/calendar/sync/outlook/authorize
```

### 7.2.4 Richieste Intervento

```
GET    /api/v1/requests                    # Lista richieste
GET    /api/v1/requests/pending             # Solo pendenti
POST   /api/v1/requests                     # Crea richiesta
GET    /api/v1/requests/:id                # Dettaglio
PATCH  /api/v1/requests/:id                # Aggiorna
POST   /api/v1/requests/:id/schedule       # Pianifica su calendario
```

### 7.2.5 Lookup e Configurazione

```
GET    /api/v1/lookup/channels             # Canali richiesta
GET    /api/v1/lookup/intervention-types   # Tipi intervento
GET    /api/v1/lookup/activity-categories   # Categorie attività
GET    /api/v1/lookup/priorities            # Priorità
GET    /api/v1/lookup/ticket-states         # Stati ticket
GET    /api/v1/lookup/intervention-states   # Stati intervento
GET    /api/v1/lookup/origins               # Origini intervento
GET    /api/v1/lookup/technicians           # Tecnici attivi
GET    /api/v1/lookup/departments           # Reparti
```

### 7.2.6 Sync Gestionale

```
POST   /api/v1/sync/clients                # Sincronizza clienti
POST   /api/v1/sync/contracts              # Sincronizza contratti
POST   /api/v1/sync/referents               # Sincronizza referenti
GET    /api/v1/sync/status                  # Stato sincronizzazione
GET    /api/v1/sync/logs                    # Log sincronizzazione
```

### 7.2.7 Knowledge Base

```
GET    /api/v1/kb/articles                  # Lista articoli
POST   /api/v1/kb/articles                  # Crea articolo
GET    /api/v1/kb/articles/:id              # Dettaglio
PATCH  /api/v1/kb/articles/:id              # Aggiorna
DELETE /api/v1/kb/articles/:id             # Elimina
GET    /api/v1/kb/search?q=...              # Ricerca full-text
GET    /api/v1/kb/categories                 # Categorie
```

### 7.2.8 Asset Management

```
GET    /api/v1/assets                       # Lista asset
POST   /api/v1/assets                        # Crea asset
GET    /api/v1/assets/:id                   # Dettaglio
PATCH  /api/v1/assets/:id                  # Aggiorna
GET    /api/v1/assets/:id/history           # Storico modifiche
GET    /api/v1/assets/:id/credentials       # Credenziali asset
POST   /api/v1/assets/:id/credentials       # Aggiungi credenziale
GET    /api/v1/credentials/:id/access       # Log accessi credenziali
```

## 7.3 Esempi Request/Response

### Esempio: Creazione Ticket

**Request:**
```http
POST /api/v1/tickets
Authorization: Bearer <token>
Content-Type: application/json

{
  "cliente_id": 123,
  "referente_id": 456,
  "canale_id": 1,
  "oggetto": "Server non risponde",
  "descrizione": "Il server principale non risponde alle richieste HTTP",
  "priorita_id": 3,
  "contratto_id": 789,
  "asset_id": 101
}
```

**Response:**
```json
{
  "id": 1001,
  "numero": "TK-2024-00123",
  "cliente_id": 123,
  "cliente_nome": "Acme S.r.l.",
  "stato": "NUOVO",
  "priorita": "ALTA",
  "scadenza_risposta": "2024-12-20T14:00:00Z",
  "scadenza_risoluzione": "2024-12-21T06:00:00Z",
  "created_at": "2024-12-20T10:00:00Z"
}
```

### Esempio: Aggiunta Riga Intervento

**Request:**
```http
POST /api/v1/interventions/500/rows
Authorization: Bearer <token>
Content-Type: application/json

{
  "categoria_id": 2,
  "descrizione": "Sostituzione disco rigido server principale",
  "quantita": 1,
  "unita_misura": "pezzi",
  "prezzo_unitario": 150.00,
  "fatturabile": true,
  "in_garanzia": false,
  "incluso_contratto": false
}
```

**Response:**
```json
{
  "id": 2001,
  "intervento_id": 500,
  "numero_riga": 1,
  "categoria": "Tecnica",
  "descrizione": "Sostituzione disco rigido server principale",
  "quantita": 1,
  "unita_misura": "pezzi",
  "prezzo_unitario": 150.00,
  "importo": 150.00,
  "created_at": "2024-12-20T15:30:00Z"
}
```

---

# 8. INTERFACCIA UTENTE

## 8.1 Design System

### 8.1.1 Colori

**Primari:**
- Primary: `#3B82F6` (Blu)
- Success: `#10B981` (Verde)
- Warning: `#F59E0B` (Arancione)
- Danger: `#EF4444` (Rosso)

**Stati:**
- Nuovo: `#3B82F6`
- In Lavorazione: `#8B5CF6`
- Chiuso: `#10B981`
- Annullato: `#EF4444`

### 8.1.2 Componenti UI

- **Card**: Container per contenuto
- **Table**: Tabelle dati con sorting/filtering
- **Modal**: Dialog per azioni
- **Form**: Input con validazione
- **Badge**: Etichette stato/priorità
- **Button**: Azioni primarie/secondarie
- **Calendar**: Vista calendario interattiva

## 8.2 Pagine Principali

### 8.2.1 Dashboard

- **KPI Cards**: Ticket aperti, interventi in corso, SLA compliance
- **Grafici**: Ticket per stato, interventi per tecnico, trend temporale
- **Lista ticket urgenti**: Ticket con priorità alta/critica
- **Calendario mini**: Prossimi appuntamenti

### 8.2.2 Lista Ticket

- **Filtri**: Stato, priorità, tecnico, cliente, data
- **Tabella**: Numero, cliente, oggetto, stato, priorità, tecnico, scadenza SLA
- **Azioni rapide**: Prendi in carico, Assegna, Chiudi
- **Pagination**: 20 ticket per pagina

### 8.2.3 Dettaglio Ticket

- **Header**: Numero, cliente, stato, priorità, SLA countdown
- **Tab Info**: Dettagli, note, messaggi, allegati, storico
- **Timeline**: Cronologia eventi
- **Azioni**: Assegna, Chiudi, Genera intervento, Annulla

### 8.2.4 Calendario

- **Vista settimanale**: Colonne giorni, righe tecnici (opzionale)
- **Eventi**: Drag & drop, resize, click per dettaglio
- **Filtri**: Tecnico, reparto, tipo, cliente
- **Creazione rapida**: Click su slot vuoto

### 8.2.5 Interventi

- **Lista**: Filtri per tecnico, cliente, stato, data
- **Dettaglio**: Header, righe attività, sessioni, tecnici, allegati
- **Form righe**: Aggiunta rapida attività
- **Timer**: Avvio/stop sessione lavoro

## 8.3 Mobile PWA

### 8.3.1 Layout Mobile

- **Bottom Navigation**: Home, Interventi, Calendario, Profilo
- **Pull to refresh**: Aggiorna dati
- **Offline indicator**: Banner quando offline
- **Swipe actions**: Azioni rapide su card

### 8.3.2 Pagine Mobile

- **Home**: Interventi giornalieri assegnati
- **Interventi**: Lista con filtri semplificati
- **Dettaglio intervento**: Scroll verticale, form compatti
- **Firma cliente**: Canvas full-screen, pulsante salva grande
- **Camera**: Accesso nativo, preview immediato

---

# 9. INTEGRAZIONI

## 9.1 Gestionale SQL Server

### 9.1.1 Import Dati

**Tabelle sorgente:**
- Clienti: `aconti` o equivalente
- Contratti: `tcontratti` o equivalente
- Referenti: Da ticket o anagrafica

**Frequenza**: Ogni 15 minuti (configurabile)

**Logica:**
```python
def sync_clients():
    # Query SQL Server per clienti modificati dopo ultimo_sync
    # Confronta con cache locale
    # Inserisci/aggiorna cache
    # Aggiorna ultimo_sync
```

### 9.1.2 Export Rapportini

**Tabelle destinazione:**
- `giinterventih` - Header intervento
- `giinterventir` - Righe attività
- `giinterventit` - Tempi lavoro
- `giinterventirt` - Tecnici aggiuntivi

**Logica:**
```python
def export_intervention(intervention_id):
    # Leggi intervento completo
    # Genera dati formato gestionale
    # Inserisci in SQL Server
    # Gestisci errori (retry)
    # Aggiorna flag sincronizzato
```

## 9.2 Calendari Esterni

### 9.2.1 Google Calendar

- **OAuth2**: Autenticazione utente
- **API**: Google Calendar API v3
- **Sync**: Bidirezionale (creazione/modifica/eliminazione)
- **Conflict**: Precedenza sistema locale

### 9.2.2 Microsoft 365 / Outlook

- **OAuth2**: Microsoft Graph API
- **Sync**: Bidirezionale
- **Conflict**: Precedenza sistema locale

## 9.3 Email

### 9.3.1 Invio Notifiche

- **SMTP**: Configurabile (Gmail, SendGrid, etc.)
- **Template**: Jinja2 o equivalente
- **Queue**: Background jobs (Celery/Bull)

### 9.3.2 Ricezione Ticket

- **IMAP/POP3**: Lettura email
- **Parsing**: Estrazione dati email → ticket
- **Allegati**: Download e allegamento

## 9.4 Monitoring (Opzionale)

### 9.4.1 Zabbix/PRTG/Nagios

- **Webhook**: Ricezione alert
- **Parsing**: Alert → ticket automatico
- **Correlazione**: Alert → asset → contratto

---

# 10. SICUREZZA

## 10.1 Autenticazione

### 10.1.1 Tecnici

- **JWT**: Token con scadenza (1 ora)
- **Refresh token**: Rinnovo automatico
- **LDAP**: Integrazione Active Directory (opzionale)
- **Locale**: Fallback database locale

### 10.1.2 Clienti (Portale)

- **Email + Password**: Hash bcrypt
- **Reset password**: Token temporaneo via email
- **2FA**: Opzionale (TOTP)

## 10.2 Autorizzazione

### 10.2.1 Ruoli

- **Admin**: Accesso completo
- **Tecnico**: Gestione ticket/interventi assegnati
- **Operatore**: Solo ticket (non interventi)
- **Cliente**: Solo propri ticket (portale)

### 10.2.2 Permessi

- **Ticket**: Creare, leggere, aggiornare, chiudere
- **Interventi**: Creare, leggere, aggiornare, chiudere
- **Calendario**: Leggere, creare, modificare propri eventi
- **Asset**: Leggere, aggiornare (solo tecnici)
- **KB**: Leggere, creare, aggiornare (solo tecnici)

## 10.3 Protezione Dati

### 10.3.1 Credenziali Cliente

- **Encryption**: AES-256
- **Key management**: Separato da database
- **Access log**: Chi accede, quando, perché

### 10.3.2 Audit Log

- **Tutte le modifiche**: Loggato in `audit_log`
- **Accessi sensibili**: Loggato in `security_audit`
- **Retention**: Configurabile (default 1 anno)

## 10.4 API Security

- **Rate limiting**: 100 req/min per utente
- **CORS**: Configurato per domini autorizzati
- **Input validation**: Pydantic/class-validator
- **SQL injection**: ORM con parametri
- **XSS**: Sanitizzazione output

---

# 11. MIGLIORAMENTI SPECIFICI IT

## 11.1 Knowledge Base

### 11.1.1 Struttura

- **Categorie gerarchiche**: Hardware, Software, Rete, Sicurezza, Guide
- **Articoli**: Titolo, contenuto rich-text, tag, visibilità
- **Versioning**: Storico versioni articoli
- **Metriche**: Visualizzazioni, valutazioni, utilizzo in ticket

### 11.1.2 Integrazione

- **Suggerimenti**: Durante risoluzione ticket, suggerisci articoli KB
- **Link ticket**: Collegamento ticket → articolo risolutivo
- **Ricerca**: Full-text su titolo e contenuto

## 11.2 Asset Management

### 11.2.1 Inventario

- **Tipi**: Server, PC, Firewall, Switch, NAS, Stampante, etc.
- **Dati**: Hostname, IP, MAC, S/N, OS, specifiche hardware
- **Stato**: Attivo, Dismissione, Guasto, Sostituito
- **Collegamento**: Asset → Contratto → Garanzia

### 11.2.2 Credenziali

- **Vault**: Criptato AES-256
- **Accesso loggato**: Chi, quando, perché, IP
- **Rotazione**: Suggerimento scadenza password
- **Collegamento**: Credenziali → Asset → Cliente

### 11.2.3 Storico

- **Modifiche**: Log tutte le modifiche configurazione
- **Timeline**: Visualizzazione cronologica
- **Collegamento**: Asset → Interventi

## 11.3 SLA Management

### 11.3.1 Definizioni

- **SLA per contratto**: Ogni contratto può avere SLA personalizzato
- **Parametri**: Tempi risposta/risoluzione per priorità
- **Finestre orarie**: Orari lavorativi configurabili
- **Pause**: SLA fermato durante attesa cliente

### 11.3.2 Tracking

- **Calcolo automatico**: Scadenze calcolate al creare ticket
- **Alert**: Notifica pre-scadenza (configurabile)
- **Report**: Compliance mensile per cliente

## 11.4 Escalation Automatica

### 11.4.1 Regole

- **Condizioni**: Priorità, tempo senza risposta, tempo senza aggiornamento
- **Azioni**: Notifica email/SMS/push, riassegnazione
- **Livelli**: Escalation multipli (tecnico → responsabile → direzione)

### 11.4.2 Notifiche

- **Template**: Personalizzabili per tipo evento
- **Multi-canale**: Email, SMS (opzionale), Push (PWA)
- **Preferenze utente**: Configurabili per utente

## 11.5 Portale Self-Service

### 11.5.1 Funzionalità Cliente

- **Apertura ticket**: Form semplificato
- **Visualizzazione**: Lista propri ticket o tutti ticket azienda
- **Messaggistica**: Chat con tecnico
- **Storico**: Interventi passati
- **Download**: Rapportini PDF
- **KB**: Accesso knowledge base pubblica

### 11.5.2 Autenticazione

- **Login**: Email + password (separato da tecnici)
- **Reset password**: Token via email
- **Permessi**: Configurabili per utente (vedere tutti ticket azienda o solo propri)

## 11.6 Progetti e Attività Programmate

### 11.6.1 Progetti

- **Creazione**: Progetto cliente con budget ore/economico
- **Milestone**: Fasi progetto con scadenze
- **Collegamento**: Progetto → Interventi
- **Tracking**: Ore consuntivate vs budget

### 11.6.2 Attività Programmate

- **Ricorrenza**: Giornaliera, settimanale, mensile, annuale
- **Generazione automatica**: Creazione richiesta intervento alla scadenza
- **Checklist**: Lista attività da verificare
- **Notifiche**: Preavviso configurabile

---

# 12. PIANO DI SVILUPPO

## 12.1 Fase 1: Foundation (3-4 settimane)

### Week 1-2: Setup & Core
- [ ] Setup progetto (FastAPI/NestJS)
- [ ] Schema database PostgreSQL completo
- [ ] Sistema autenticazione JWT
- [ ] API CRUD base per lookup tables
- [ ] Docker setup per sviluppo

### Week 3-4: Sync Gestionale
- [ ] Connessione SQL Server gestionale
- [ ] Import clienti/contratti/referenti
- [ ] Scheduler sincronizzazione periodica
- [ ] Logging e gestione errori sync
- [ ] Cache invalidation strategy

## 12.2 Fase 2: Ticket Management (2-3 settimane)

### Week 5-6: Ticket Core
- [ ] CRUD Ticket completo
- [ ] Sistema stati e transizioni
- [ ] Note e messaggi
- [ ] Allegati
- [ ] Assegnazione tecnici
- [ ] Filtri e ricerca avanzata
- [ ] Dashboard operatore

### Week 7: Ticket Advanced
- [ ] Chiusura con opzioni
- [ ] Generazione richiesta intervento
- [ ] SLA tracking
- [ ] Notifiche (email/push)

## 12.3 Fase 3: Interventi (3-4 settimane)

### Week 8-9: Intervento Core
- [ ] Creazione intervento da varie origini
- [ ] Gestione righe attività
- [ ] Sessioni di lavoro (tempi)
- [ ] Team tecnici
- [ ] Allegati e foto

### Week 10-11: Rapportino
- [ ] Workflow chiusura
- [ ] Firma cliente (canvas)
- [ ] Preview rapportino
- [ ] Export PDF
- [ ] Sincronizzazione a gestionale
- [ ] Gestione errori export

## 12.4 Fase 4: Calendario (2-3 settimane)

### Week 12-13: Calendario Core
- [ ] Vista calendario (FullCalendar o custom)
- [ ] CRUD eventi
- [ ] Drag & drop
- [ ] Assegnazione multipla tecnici
- [ ] Filtri per tecnico/reparto
- [ ] Colori per tipo/stato

### Week 14: Calendar Sync
- [ ] Google Calendar integration
- [ ] Microsoft 365/Outlook integration
- [ ] Sync bidirezionale
- [ ] Conflict resolution

## 12.5 Fase 5: Mobile PWA (3-4 settimane)

### Week 15-16: PWA Core
- [ ] Setup PWA (service worker)
- [ ] Layout responsive
- [ ] Offline storage (IndexedDB)
- [ ] Background sync
- [ ] Push notifications

### Week 17-18: Mobile Features
- [ ] Firma cliente touch
- [ ] Camera integration
- [ ] Timer lavoro
- [ ] Geolocalizzazione
- [ ] Quick actions

## 12.6 Fase 6: Moduli Avanzati (3-4 settimane)

### Week 19-20: Knowledge Base
- [ ] CRUD articoli
- [ ] Categorie gerarchiche
- [ ] Ricerca full-text
- [ ] Suggerimenti durante ticket
- [ ] Sezione pubblica

### Week 21-22: Asset Management
- [ ] CRUD asset
- [ ] Vault credenziali
- [ ] Storico modifiche
- [ ] Collegamento a ticket/interventi

### Week 23-24: SLA & Escalation
- [ ] Definizioni SLA
- [ ] Tracking automatico
- [ ] Alert pre-scadenza
- [ ] Regole escalation
- [ ] Notifiche multi-canale

## 12.7 Fase 7: Portale Cliente (2 settimane)

### Week 25-26: Portale
- [ ] Autenticazione separata
- [ ] Apertura ticket
- [ ] Visualizzazione ticket
- [ ] Messaggistica
- [ ] Download rapportini
- [ ] KB pubblica

## 12.8 Fase 8: Polish & Deploy (2 settimane)

### Week 27-28: Refinement
- [ ] Performance optimization
- [ ] Security audit
- [ ] Testing E2E
- [ ] Documentazione API
- [ ] Migration tools
- [ ] Deploy production

---

# APPENDICE: PROMPT PER AI

## Prompt Completo per Generazione Codice

```
Devo sviluppare un sistema web per la gestione dell'assistenza tecnica di una società informatica.

## Contesto
Il sistema deve gestire l'intero ciclo di vita dalla richiesta del cliente al rapportino di intervento finale, 
con sincronizzazione bidirezionale con un gestionale esterno (SQL Server).

## Stack Tecnologico
- Backend: Python/FastAPI (o Node.js/NestJS)
- Database locale: PostgreSQL 15+
- Database gestionale: SQL Server (read + write rapportini)
- Frontend: React 18+ (o Vue 3)
- Mobile: PWA con supporto offline

## Entità Principali

### Ticket
- Canali richiesta: {TELEFONO, EMAIL, WEBAPP, VOCE, PORTALE, MONITORING}
- Stati: {NUOVO, PRESO_CARICO, IN_LAVORAZIONE, SCHEDULATO, CHIUSO, ANNULLATO}
- Chiusura: diretta | con intervento immediato | con richiesta intervento
- SLA tracking automatico

### Intervento
- Origini: {DA_TICKET, DA_PIANIFICAZIONE, DA_PROGETTO, SPONTANEO, DA_CONTRATTO}
- Tipi: {CLIENTE, LABORATORIO, REMOTO, TELEFONICO}
- Categorie attività: {TECNICA, SISTEMISTICA, GESTIONALE, CENTRALINO, SECURITY, CONSULENZA, SVILUPPO, FORMAZIONE}
- Struttura: header + N righe attività + N sessioni tempo + N tecnici team
- Multi-giorno: una sessione per ogni giorno lavorato
- Firma cliente mobile (canvas touch)

### Calendario
- Eventi collegati a richieste/interventi
- Assegnazione multipla tecnici
- Sincronizzazione con Google/Outlook
- Colori per tipo/stato/tecnico

### Knowledge Base
- Articoli con categorie gerarchiche
- Ricerca full-text
- Link a ticket risolti
- Sezione pubblica per FAQ clienti

### Asset Management
- Inventario infrastruttura cliente
- Storico modifiche
- Vault credenziali sicuro (AES-256)
- Collegamento a contratti/garanzie

## Funzionalità Richieste

### Core
1. CRUD completo per tutte le entità
2. Workflow stati con validazioni
3. Filtri e ricerca avanzata
4. Dashboard per operatori e tecnici

### Integrazione Gestionale
1. Sync periodico clienti/contratti (cache locale)
2. Export rapportini chiusi a gestionale
3. Gestione conflitti e retry

### Mobile
1. PWA con supporto offline
2. Firma cliente su canvas touch
3. Foto da fotocamera
4. Timer lavoro integrato
5. Geolocalizzazione (opzionale)

### Calendario
1. Vista giorno/settimana/mese
2. Drag & drop eventi
3. Sync calendario esterno
4. Notifiche/reminder

### SLA Management
1. Definizioni SLA per contratto
2. Tracking automatico tempi
3. Pause per attesa cliente
4. Alert pre-scadenza
5. Report compliance

### Escalation
1. Regole configurabili
2. Notifiche multi-canale
3. Riassegnazione automatica

## Modello Dati
[Inserire qui le tabelle SQL o riferimento a schema completo]

## API Design
Seguire pattern RESTful con:
- Versioning: /api/v1/
- Autenticazione: JWT Bearer
- Pagination: offset/limit
- Filtering: query params
- Errori: RFC 7807 Problem Details

## Vincoli e Note
- Evitare duplicazione dati tra sistema locale e gestionale
- Il gestionale è master per: clienti, contratti, referenti
- Il sistema locale è master per: ticket, interventi in corso
- Al momento della chiusura rapportino, i dati vengono "congelati" e sincronizzati
- Supporto offline completo per mobile
- Audit log completo di tutte le operazioni

## Output Richiesto
[Specificare cosa vuoi generare: schema DB, API endpoint, componente frontend, etc.]
```

---

# CONCLUSIONI

Questo documento fornisce una specifica completa per lo sviluppo del sistema di gestione assistenza IT. 

**Prossimi passi:**
1. Revisione documento con stakeholder
2. Approvazione stack tecnologico
3. Setup ambiente sviluppo
4. Inizio Fase 1 (Foundation)

**Note finali:**
- Il sistema deve essere modulare e estendibile
- Priorità alla stabilità e performance
- UX intuitiva per ridurre curva apprendimento
- Documentazione completa per manutenzione futura

---

**Versione documento:** 1.0  
**Ultima modifica:** Dicembre 2024  
**Autore:** Analisi sistema esistente + miglioramenti IT

