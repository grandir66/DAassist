# Struttura Clienti - DAAssist

## Panoramica

La gestione clienti è stata estesa per supportare:
- **Stati e classificazioni** dei clienti
- **Sedi operative multiple** (oltre alla sede legale)
- **Rubrica contatti** con referenti per sede
- **Orari di servizio** personalizzati
- **Referente IT principale** collegato

## Struttura Database

### 1. Tabella `cache_clienti` (Clienti)

**Sede Legale:**
- `ragione_sociale` - Ragione sociale completa
- `codice_gestionale` - Codice dal gestionale esterno
- `partita_iva`, `codice_fiscale`
- `indirizzo`, `cap`, `citta`, `provincia`, `nazione`
- `telefono`, `email`, `pec`, `sito_web`

**Gestione Cliente:**
- `stato_cliente` - ATTIVO | SOSPESO | INATTIVO | PROSPECT
- `classificazione` - VIP | PREMIUM | STANDARD | BASIC | ENTERPRISE
- `referente_it_id` - FK a `cache_referenti` (referente IT principale)

**Servizio:**
- `orari_servizio` - JSON con orari per giorno:
  ```json
  {
    "lunedi": "08:00-18:00",
    "martedi": "08:00-18:00",
    "mercoledi": "08:00-18:00",
    "giovedi": "08:00-18:00",
    "venerdi": "08:00-17:00",
    "sabato": null,
    "domenica": null
  }
  ```

**Ricerca:**
- `nomi_alternativi` - Nomi/acronimi separati da virgola per ricerca
  - Es: "ACME SPA, Acme Corp, ACME"

**Sync:**
- `ultimo_sync` - Timestamp ultima sincronizzazione gestionale
- `hash_dati` - SHA256 per rilevare modifiche
- `note` - Note generali sul cliente

### 2. Tabella `sedi_cliente` (Sedi Operative)

Gestisce le sedi operative del cliente (filiali, stabilimenti, uffici remoti).

**Identificazione:**
- `cliente_id` - FK a `cache_clienti`
- `nome_sede` - Es: "Sede Milano", "Filiale Roma", "Stabilimento Torino"
- `codice_sede` - Codice interno cliente (opzionale)

**Indirizzo:**
- `indirizzo` - Via e numero civico **(obbligatorio)**
- `cap`, `citta` **(obbligatorio)**, `provincia`, `nazione`

**Contatti:**
- `telefono` - Telefono sede
- `email` - Email generale sede

**Servizio:**
- `orari_servizio` - JSON con orari specifici sede (se diversi dal cliente)
- `note` - Note specifiche sulla sede

**Use Case:**
- Un intervento può essere fatto presso una sede specifica
- Ogni referente può essere associato a una sede
- Ricerca interventi per sede
- Report per sede

### 3. Tabella `cache_referenti` (Rubrica Contatti)

Rubrica completa dei contatti del cliente.

**Anagrafica:**
- `cliente_id` - FK a `cache_clienti` **(obbligatorio)**
- `sede_id` - FK a `sedi_cliente` (opzionale, se referente di una sede specifica)
- `nome`, `cognome` **(obbligatori, indicizzati)**
- `ruolo` - Es: "IT Manager", "Amministratore", "Responsabile Acquisti"

**Contatti:**
- `telefono` - Telefono diretto
- `cellulare` - Cellulare
- `interno_telefonico` - Interno centralino (es: "101")
- `email` **(indicizzato per ricerca veloce)**

**Flags:**
- `contatto_principale` - Flag contatto principale (boolean 0/1)
- `referente_it` - Flag referente IT (boolean 0/1)
- `riceve_notifiche` - Riceve notifiche sistema (boolean 0/1)

**Altro:**
- `note` - Note sul referente
- `codice_gestionale` - Codice dal gestionale (opzionale)

### 4. Tabelle Lookup

#### `lookup_stati_cliente`
| Codice | Descrizione | Colore | Ordine |
|--------|-------------|--------|--------|
| PROSPECT | Prospect (Potenziale Cliente) | #3B82F6 | 0 |
| ATTIVO | Cliente Attivo | #10B981 | 1 |
| SOSPESO | Cliente Sospeso | #F59E0B | 2 |
| INATTIVO | Cliente Inattivo | #6B7280 | 3 |

#### `lookup_classificazioni_cliente`
| Codice | Descrizione | Colore | Ordine |
|--------|-------------|--------|--------|
| ENTERPRISE | Enterprise | #059669 | 0 |
| VIP | Cliente VIP | #8B5CF6 | 1 |
| PREMIUM | Cliente Premium | #EC4899 | 2 |
| STANDARD | Cliente Standard | #3B82F6 | 3 |
| BASIC | Cliente Basic | #6B7280 | 4 |

## Relazioni

```
cache_clienti (1) ----< (N) sedi_cliente
     |
     | (1)
     |
     v
cache_referenti (referente_it_id) - Referente IT Principale
     ^
     |
     | (N)
     |
cache_referenti (cliente_id) - Tutti i referenti del cliente
     |
     | (N)
     |
     v (1)
sedi_cliente (sede_id) - Sede di appartenenza del referente
```

## Use Cases

### 1. Creazione Cliente
```python
# 1. Crea cliente
cliente = CacheClienti(
    ragione_sociale="ACME SPA",
    codice_gestionale="CLI001",
    stato_cliente="ATTIVO",
    classificazione="PREMIUM",
    orari_servizio='{"lunedi": "08:00-18:00", ...}',
    nomi_alternativi="ACME, Acme Corp"
)

# 2. Aggiungi sedi
sede_milano = SediCliente(
    cliente_id=cliente.id,
    nome_sede="Sede Milano",
    citta="Milano",
    indirizzo="Via Roma 1"
)

sede_roma = SediCliente(
    cliente_id=cliente.id,
    nome_sede="Filiale Roma",
    citta="Roma",
    indirizzo="Via del Corso 100"
)

# 3. Aggiungi referenti
ref_it = CacheReferenti(
    cliente_id=cliente.id,
    sede_id=sede_milano.id,  # Lavora a Milano
    nome="Mario",
    cognome="Rossi",
    ruolo="IT Manager",
    email="mario.rossi@acme.it",
    cellulare="+39 333 1234567",
    interno_telefonico="101",
    referente_it=1,
    contatto_principale=1
)

# 4. Collega referente IT al cliente
cliente.referente_it_id = ref_it.id
```

### 2. Ricerca Avanzata

**Per nome alternativo:**
```sql
SELECT * FROM cache_clienti
WHERE
  ragione_sociale ILIKE '%acme%'
  OR nomi_alternativi ILIKE '%acme%'
```

**Referenti IT:**
```sql
SELECT r.*, c.ragione_sociale, s.nome_sede
FROM cache_referenti r
JOIN cache_clienti c ON r.cliente_id = c.id
LEFT JOIN sedi_cliente s ON r.sede_id = s.id
WHERE r.referente_it = 1
ORDER BY c.ragione_sociale, r.cognome
```

**Clienti VIP attivi:**
```sql
SELECT * FROM cache_clienti
WHERE stato_cliente = 'ATTIVO'
  AND classificazione = 'VIP'
```

### 3. Intervento presso sede specifica

```python
# Intervento da fare presso la filiale di Roma
intervento = Intervento(
    cliente_id=cliente.id,
    sede_id=sede_roma.id,  # Specifica la sede
    titolo="Installazione server",
    ...
)
```

### 4. Orari di servizio

**Check orari cliente:**
```python
import json
from datetime import datetime

# Carica orari
orari = json.loads(cliente.orari_servizio)
giorno_settimana = datetime.now().strftime("%A").lower()  # "lunedi", "martedi", ...

orario_oggi = orari.get(giorno_settimana)
if orario_oggi:
    print(f"Orari oggi: {orario_oggi}")  # "08:00-18:00"
else:
    print("Cliente non operativo oggi")
```

## API Endpoints da Implementare

### Clienti
- `GET /api/v1/clients` - Lista clienti (con filtri)
- `GET /api/v1/clients/{id}` - Dettaglio cliente
- `POST /api/v1/clients` - Crea cliente
- `PUT /api/v1/clients/{id}` - Aggiorna cliente
- `DELETE /api/v1/clients/{id}` - Disattiva cliente

### Sedi
- `GET /api/v1/clients/{client_id}/sites` - Sedi del cliente
- `GET /api/v1/sites/{id}` - Dettaglio sede
- `POST /api/v1/clients/{client_id}/sites` - Crea sede
- `PUT /api/v1/sites/{id}` - Aggiorna sede
- `DELETE /api/v1/sites/{id}` - Elimina sede

### Referenti/Rubrica
- `GET /api/v1/clients/{client_id}/contacts` - Contatti del cliente
- `GET /api/v1/sites/{site_id}/contacts` - Contatti della sede
- `GET /api/v1/contacts/{id}` - Dettaglio contatto
- `POST /api/v1/clients/{client_id}/contacts` - Crea contatto
- `PUT /api/v1/contacts/{id}` - Aggiorna contatto
- `DELETE /api/v1/contacts/{id}` - Elimina contatto
- `GET /api/v1/contacts/it-referents` - Lista tutti i referenti IT

### Lookup
- `GET /api/v1/lookup/client-states` - Stati cliente
- `GET /api/v1/lookup/client-classifications` - Classificazioni

## Frontend da Implementare

### Pagina Clienti
- Lista clienti con filtri (stato, classificazione, ricerca)
- Dettaglio cliente con tabs:
  - **Dati Cliente**: anagrafica, contatti, sede legale
  - **Sedi**: lista sedi operative
  - **Rubrica**: lista contatti/referenti
  - **Contratti**: contratti attivi
  - **Ticket**: ticket del cliente
  - **Interventi**: storico interventi

### Modale Gestione Sedi
- Form creazione/modifica sede
- Lista sedi con mappa (opzionale)

### Rubrica Contatti
- Lista contatti con ricerca
- Badge per:
  - Contatto principale
  - Referente IT
  - Riceve notifiche
- Click-to-call, click-to-email

## Note Tecniche

### Dipendenza Circolare
La relazione `cache_clienti.referente_it_id → cache_referenti.id` crea una dipendenza circolare, risolta con `use_alter=True` nella foreign key.

### Indici Performance
Creati indici su:
- `cache_clienti.stato_cliente`
- `cache_referenti.nome`, `cognome`, `email`
- `sedi_cliente.cliente_id`

### JSON Fields
I campi `orari_servizio` usano formato JSON per flessibilità. Validare formato in Pydantic schemas.

### Soft Delete
Tutte le tabelle ereditano da `BaseModel` con campo `attivo` per soft delete.
