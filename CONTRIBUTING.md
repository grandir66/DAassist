# Contribuire a DAAssist

Grazie per l'interesse nel contribuire a DAAssist! Questo documento fornisce le linee guida per contribuire al progetto.

## Come Contribuire

### Segnalare Bug

Se trovi un bug, apri una issue su GitHub includendo:

1. **Descrizione chiara** del problema
2. **Passi per riprodurre** il bug
3. **Comportamento atteso** vs **comportamento attuale**
4. **Ambiente**: OS, versione Docker, browser (per frontend)
5. **Log** se disponibili

### Proporre Feature

Per proporre nuove funzionalità:

1. Apri una **issue** descrivendo la feature
2. Spiega il **caso d'uso** e i benefici
3. Discuti l'implementazione con i maintainer prima di iniziare

### Pull Request

1. **Fork** il repository
2. Crea un **branch** per la tua feature:
   ```bash
   git checkout -b feature/nome-feature
   ```
3. Fai le tue modifiche seguendo le linee guida di stile
4. **Testa** le modifiche
5. **Commit** con messaggi descrittivi:
   ```bash
   git commit -m "Add: descrizione breve della feature"
   ```
6. **Push** al tuo fork:
   ```bash
   git push origin feature/nome-feature
   ```
7. Apri una **Pull Request** verso `main`

## Linee Guida di Sviluppo

### Backend (Python/FastAPI)

- Usa **type hints** per tutti i parametri e return types
- Segui **PEP 8** per lo stile del codice
- Documenta le funzioni con **docstrings**
- Scrivi test per le nuove feature
- Usa **Pydantic** per la validazione dati
- Mantieni la separazione tra **API, Repository, Models, Schemas**

Esempio:
```python
def get_ticket_by_id(db: Session, ticket_id: int) -> Optional[Ticket]:
    """
    Retrieve a ticket by ID.

    Args:
        db: Database session
        ticket_id: ID of the ticket

    Returns:
        Ticket object if found, None otherwise
    """
    return db.query(Ticket).filter_by(id=ticket_id, attivo=True).first()
```

### Frontend (React/TypeScript)

- Usa **TypeScript** con strict mode
- Componenti **funzionali** con hooks
- Mantieni componenti **piccoli e riutilizzabili**
- Usa **TailwindCSS** per lo styling
- Gestisci lo stato con **Zustand** quando necessario
- Documenta props complessi con commenti

Esempio:
```typescript
interface TicketCardProps {
  ticket: Ticket;
  onEdit?: (id: number) => void;
  onDelete?: (id: number) => void;
}

export function TicketCard({ ticket, onEdit, onDelete }: TicketCardProps) {
  // Implementation
}
```

### Database

- Le migrazioni devono essere **reversibili**
- Usa `alembic` per tutte le modifiche schema
- Testa le migrazioni in ambiente di sviluppo
- Documenta le modifiche nel commit

```bash
# Crea migrazione
alembic revision --autogenerate -m "Add column xyz to table abc"

# Applica migrazione
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Convenzioni Git

### Branch Naming

- `feature/nome-feature` - Nuove funzionalità
- `bugfix/nome-bug` - Fix di bug
- `hotfix/nome-fix` - Fix urgenti per produzione
- `refactor/nome` - Refactoring codice
- `docs/nome` - Modifiche documentazione

### Commit Messages

Usa il formato:

```
<type>: <subject>

<body (opzionale)>
```

**Types:**
- `feat`: Nuova feature
- `fix`: Bug fix
- `docs`: Modifiche documentazione
- `style`: Formattazione, missing semicolons, etc
- `refactor`: Refactoring codice
- `test`: Aggiunta test
- `chore`: Manutenzione, dependency updates

Esempi:
```bash
feat: Add ticket priority filter to dashboard
fix: Correct date validation in intervention form
docs: Update installation instructions for LXC
refactor: Extract duplicate code in client repository
```

## Testing

### Backend Tests

```bash
cd backend
pytest
pytest --cov=app  # Con coverage
```

### Frontend Tests

```bash
cd frontend
npm test
npm run test:coverage
```

## Code Review

Le PR verranno revisionate per:

- ✅ Codice funzionante e testato
- ✅ Aderenza alle linee guida di stile
- ✅ Documentazione adeguata
- ✅ Nessun codice hardcoded o credenziali
- ✅ Performance accettabili
- ✅ Compatibilità con il sistema esistente

## Domande?

Se hai domande:

- Apri una **Discussion** su GitHub
- Scrivi una **issue** con label `question`
- Contatta i maintainer

Grazie per il tuo contributo! 🙏
