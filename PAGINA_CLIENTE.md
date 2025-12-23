# Pagina Dettaglio Cliente - DAAssist

## Overview

Pagina completa per la visualizzazione dei dati del cliente con layout organizzato in tab, che include tutte le informazioni rilevanti: dati anagrafici, sedi operative, contatti e contratti.

## Percorso

**URL:** `/clients/:id`

**Accesso:** Dalla lista clienti (`/clients`), cliccando su qualsiasi card cliente

## Struttura

La pagina è organizzata in **4 tab principali**:

### 1. Informazioni Generali

Visualizza tutti i dati anagrafici e informativi del cliente:

- **Dati Anagrafici:**
  - Ragione Sociale
  - Partita IVA
  - Codice Fiscale
  - Nomi Alternativi (per ricerca)

- **Sede Legale:**
  - Indirizzo completo
  - CAP, Città, Provincia

- **Contatti:**
  - Telefono
  - Email
  - PEC
  - Sito Web (con link cliccabile)

- **Orari di Servizio:**
  - Orari per ogni giorno della settimana
  - Visualizzati in formato tabellare

- **Note:**
  - Note generali sul cliente
  - Campo multi-linea

- **Badge Stato e Classificazione:**
  - **Stati:** ATTIVO, SOSPESO, INATTIVO, PROSPECT
  - **Classificazioni:** VIP, PREMIUM, ENTERPRISE, STANDARD, BASIC
  - Ogni badge ha un colore distintivo

### 2. Sedi Operative

Visualizza tutte le sedi operative del cliente (oltre alla sede legale):

- Layout a card (2 colonne su desktop)
- Per ogni sede:
  - Nome sede
  - Codice sede
  - Indirizzo completo
  - Contatti (telefono, email)
  - Orari specifici (se diversi da quelli generali)
  - Note specifiche della sede

**Messaggio vuoto:** Se non ci sono sedi operative registrate

### 3. Contatti/Rubrica

Tabella completa con tutti i contatti del cliente:

| Nome | Ruolo | Contatti | Flags |
|------|-------|----------|-------|
| Nome Cognome | Ruolo | Tel, Cell, Interno, Email | Badge |

**Caratteristiche:**
- **Badge Principale:** Indica il contatto principale (stella)
- **Badge IT:** Indica i referenti IT
- **Badge Notifiche:** Indica chi riceve le notifiche
- **Interno Telefonico:** Numero interno centralino
- **Link Email:** Email cliccabile (mailto)
- **Collegamento Sede:** Ogni contatto può essere associato a una sede specifica

### 4. Contratti

Tabella con tutti i contratti del cliente:

| Codice | Descrizione | Periodo | Ore | Stato |
|--------|-------------|---------|-----|-------|
| COD123 | Assistenza Premium | 01/01/24 - 31/12/24 | 50/100 | Attivo |

**Caratteristiche:**
- **Periodo:** Data inizio e fine contratto
- **Ore:**
  - Ore utilizzate / Ore incluse
  - Barra di progresso colorata:
    - Verde: < 75%
    - Giallo: 75-90%
    - Rosso: > 90%
- **Stato:** Badge attivo/inattivo

## Colori Badge

### Stati Cliente
- **ATTIVO:** Verde (#10B981)
- **SOSPESO:** Giallo (#F59E0B)
- **INATTIVO:** Grigio (#6B7280)
- **PROSPECT:** Blu (#3B82F6)

### Classificazioni
- **VIP:** Viola (#8B5CF6)
- **PREMIUM:** Rosa (#EC4899)
- **ENTERPRISE:** Verde smeraldo (#059669)
- **STANDARD:** Blu (#3B82F6)
- **BASIC:** Grigio (#6B7280)

## API Endpoints Utilizzati

```typescript
// Client data
GET /api/v1/clients/:id

// Sedi operative
GET /api/v1/clients/:id/sites

// Contatti/Rubrica
GET /api/v1/clients/:id/contacts

// Contratti
GET /api/v1/clients/:id/contratti
```

## Stati Loading

- **Loading iniziale:** Spinner centrale durante il caricamento
- **Cliente non trovato:** Messaggio con pulsante "Torna ai Clienti"
- **Tab vuoti:** Messaggi specifici per ogni tipo di dato mancante

## Navigazione

- **Pulsante Indietro:** In alto a sinistra, ritorna alla lista clienti
- **Tab Navigation:** Click sui tab per navigare tra le sezioni
- **Counter Badge:** Ogni tab mostra il numero di elementi (es: "Sedi Operative (3)")

## File Modificati/Creati

### File Creati:
1. `/frontend/src/pages/ClientDetail.tsx` - Pagina principale
2. `/PAGINA_CLIENTE.md` - Questa documentazione

### File Modificati:
1. `/frontend/src/api/clients.ts` - Aggiunti nuovi tipi e metodi API
   - `SedeCliente` interface
   - `Referente` interface aggiornata con nuovi campi
   - `Cliente` interface con campi estesi
   - Metodi: `getSedi()`, `getContatti()`

2. `/frontend/src/App.tsx` - Aggiunta route
   - Import `ClientDetail`
   - Route `/clients/:id`

3. `/frontend/src/pages/Clients.tsx` - Aggiunto link
   - Click sulla card cliente naviga al dettaglio

## Responsive Design

- **Desktop:** Layout a 2 colonne per card
- **Tablet:** Layout responsive
- **Mobile:** Singola colonna, tabelle scrollabili orizzontalmente

## Test con Dati di Prova

Per testare la pagina, sono disponibili 5 clienti di esempio:

1. **TechSolution S.r.l.** (ID: 1) - PREMIUM/ATTIVO
   - 1 sede operativa a Roma
   - 3 contatti

2. **Studio Rossi** (ID: 2) - STANDARD/ATTIVO
   - 2 contatti

3. **Beta Manifatture** (ID: 3) - ENTERPRISE/ATTIVO
   - 3 sedi operative (Torino, Milano, Logistica)
   - 6 contatti distribuiti tra le sedi

4. **Alpha Startup** (ID: 4) - BASIC/PROSPECT
   - 1 contatto

5. **Hotel Continental** (ID: 5) - STANDARD/SOSPESO
   - 2 contatti

## Come Accedere

1. Avvia l'applicazione: `./start.sh`
2. Login con credenziali: `admin` / `admin`
3. Menu → Clienti
4. Click su qualsiasi cliente
5. Naviga tra i tab per esplorare i dati

## URL Diretti per Test

- http://localhost:3000/clients/1 - TechSolution
- http://localhost:3000/clients/2 - Studio Rossi
- http://localhost:3000/clients/3 - Beta Manifatture
- http://localhost:3000/clients/4 - Alpha Startup
- http://localhost:3000/clients/5 - Hotel Continental
