from typing import List, Optional, Tuple
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, func, and_

from app.models.intervention import Intervento, InterventoRiga, InterventoSessione
from app.schemas.intervention import (
    InterventoCreate,
    InterventoUpdate,
    AttivitaInterventoCreate,
    SessioneCreate,
    SessioneUpdate,
    RigaAttivitaUpdate,
)


class InterventionRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(
        self,
        skip: int = 0,
        limit: int = 20,
        stato_id: Optional[int] = None,
        tipo_id: Optional[int] = None,
        tecnico_id: Optional[int] = None,
        cliente_id: Optional[int] = None,
        data_from: Optional[datetime] = None,
        data_to: Optional[datetime] = None,
        search: Optional[str] = None,
    ) -> Tuple[List[Intervento], int]:
        """Get all interventions with filters"""
        query = self.db.query(Intervento).options(
            joinedload(Intervento.cliente),
            joinedload(Intervento.tecnico),
            joinedload(Intervento.tipo_intervento),
            joinedload(Intervento.stato),
            joinedload(Intervento.origine),
        )

        # Apply filters
        query = query.filter(Intervento.attivo == True)

        if stato_id:
            query = query.filter(Intervento.stato_id == stato_id)

        if tipo_id:
            query = query.filter(Intervento.tipo_id == tipo_id)

        if tecnico_id:
            query = query.filter(Intervento.tecnico_id == tecnico_id)

        if cliente_id:
            query = query.filter(Intervento.cliente_id == cliente_id)

        if data_from:
            query = query.filter(Intervento.data_inizio >= data_from)

        if data_to:
            query = query.filter(Intervento.data_inizio <= data_to)

        if search:
            search_filter = f"%{search}%"
            query = query.filter(
                or_(
                    Intervento.numero.ilike(search_filter),
                    Intervento.descrizione.ilike(search_filter),
                )
            )

        # Get total count
        total = query.count()

        # Apply pagination and ordering
        interventi = (
            query.order_by(Intervento.data_inizio.desc()).offset(skip).limit(limit).all()
        )

        return interventi, total

    def get_by_id(self, intervento_id: int) -> Optional[Intervento]:
        """Get intervention by ID with relationships"""
        return (
            self.db.query(Intervento)
            .options(
                joinedload(Intervento.cliente),
                joinedload(Intervento.tecnico),
                joinedload(Intervento.tipo_intervento),
                joinedload(Intervento.stato),
                joinedload(Intervento.origine),
            )
            .filter(Intervento.id == intervento_id, Intervento.attivo == True)
            .first()
        )

    def get_by_numero(self, numero: str) -> Optional[Intervento]:
        """Get intervention by numero"""
        return (
            self.db.query(Intervento)
            .filter(Intervento.numero == numero, Intervento.attivo == True)
            .first()
        )

    def create(self, intervento_data: InterventoCreate) -> Intervento:
        """Create new intervention"""
        # Generate numero
        numero = self._generate_intervention_number()

        intervento = Intervento(
            numero=numero,
            **intervento_data.model_dump(),
        )

        self.db.add(intervento)
        self.db.commit()
        self.db.refresh(intervento)

        return intervento

    def update(self, intervento: Intervento, update_data: InterventoUpdate) -> Intervento:
        """Update intervention"""
        update_dict = update_data.model_dump(exclude_unset=True)

        for field, value in update_dict.items():
            setattr(intervento, field, value)

        intervento.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(intervento)

        return intervento

    def start(self, intervento: Intervento, note_avvio: Optional[str] = None) -> Intervento:
        """Start intervention"""
        from app.models.lookup import LookupStatiIntervento

        stato_in_corso = (
            self.db.query(LookupStatiIntervento).filter_by(codice="IN_CORSO").first()
        )

        if not stato_in_corso:
            raise ValueError("Stato 'IN_CORSO' non trovato")

        intervento.stato_id = stato_in_corso.id
        intervento.data_inizio = datetime.utcnow()

        if note_avvio:
            intervento.note_interne = (
                f"{intervento.note_interne}\n\n[AVVIO] {note_avvio}"
                if intervento.note_interne
                else f"[AVVIO] {note_avvio}"
            )

        intervento.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(intervento)

        return intervento

    def complete(
        self,
        intervento: Intervento,
        descrizione_lavoro: str,
        firma_cliente: Optional[str] = None,
        firma_nome: Optional[str] = None,
        firma_ruolo: Optional[str] = None,
    ) -> Intervento:
        """Complete intervention"""
        from app.models.lookup import LookupStatiIntervento

        stato_completato = (
            self.db.query(LookupStatiIntervento).filter_by(codice="COMPLETATO").first()
        )

        if not stato_completato:
            raise ValueError("Stato 'COMPLETATO' non trovato")

        intervento.stato_id = stato_completato.id
        intervento.data_fine = datetime.utcnow()
        intervento.descrizione_lavoro = descrizione_lavoro
        intervento.firma_cliente = firma_cliente
        intervento.firma_nome = firma_nome
        intervento.firma_ruolo = firma_ruolo
        if firma_cliente:
            intervento.firma_data = datetime.utcnow()
        intervento.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(intervento)

        return intervento

    def add_attivita(
        self, intervento_id: int, attivita_data: AttivitaInterventoCreate
    ) -> InterventoRiga:
        """Add activity to intervention"""
        from app.models.lookup import LookupCategorieAttivita

        categoria = (
            self.db.query(LookupCategorieAttivita)
            .filter_by(id=attivita_data.categoria_id)
            .first()
        )

        if not categoria:
            raise ValueError("Categoria non trovata")

        # Use provided price or default from category
        prezzo = (
            attivita_data.prezzo_unitario
            if attivita_data.prezzo_unitario is not None
            else categoria.prezzo_unitario_default
        )

        # Get last row number
        last_riga = (
            self.db.query(InterventoRiga)
            .filter_by(intervento_id=intervento_id)
            .order_by(InterventoRiga.numero_riga.desc())
            .first()
        )
        numero_riga = (last_riga.numero_riga + 1) if last_riga else 1

        # Convert minutes to hours for quantita
        quantita = attivita_data.durata / 60.0

        attivita = InterventoRiga(
            intervento_id=intervento_id,
            numero_riga=numero_riga,
            categoria_id=attivita_data.categoria_id,
            descrizione=attivita_data.descrizione,
            quantita=quantita,
            unita_misura="ore",
            prezzo_unitario=prezzo if prezzo else 0,
        )

        self.db.add(attivita)
        self.db.commit()
        self.db.refresh(attivita)

        return attivita

    def delete(self, intervento: Intervento) -> None:
        """Soft delete intervention"""
        intervento.attivo = False
        intervento.updated_at = datetime.utcnow()

        self.db.commit()

    # Sessioni Lavoro
    def get_sessioni(self, intervento_id: int) -> List[InterventoSessione]:
        """Get all work sessions for an intervention"""
        return (
            self.db.query(InterventoSessione)
            .filter(
                InterventoSessione.intervento_id == intervento_id,
                InterventoSessione.attivo == True,
            )
            .order_by(InterventoSessione.data.desc(), InterventoSessione.ora_inizio.desc())
            .all()
        )

    def add_sessione(
        self, intervento_id: int, tecnico_id: int, sessione_data
    ) -> InterventoSessione:
        """Add work session to intervention"""
        from app.models.intervention import InterventoSessione

        # Calculate duration if ora_fine is provided
        durata_minuti = None
        if sessione_data.ora_fine:
            # Convert time to minutes and calculate difference
            inizio_minuti = (
                sessione_data.ora_inizio.hour * 60 + sessione_data.ora_inizio.minute
            )
            fine_minuti = sessione_data.ora_fine.hour * 60 + sessione_data.ora_fine.minute
            durata_minuti = fine_minuti - inizio_minuti
            if durata_minuti < 0:
                durata_minuti += 24 * 60  # Handle overnight sessions

        sessione = InterventoSessione(
            intervento_id=intervento_id,
            tecnico_id=tecnico_id,
            data=sessione_data.data,
            ora_inizio=sessione_data.ora_inizio,
            ora_fine=sessione_data.ora_fine,
            durata_minuti=durata_minuti,
            tipo_intervento_id=sessione_data.tipo_intervento_id,
            km_percorsi=sessione_data.km_percorsi,
            tempo_viaggio_minuti=sessione_data.tempo_viaggio_minuti,
            note=sessione_data.note,
            attivo=True,
        )

        self.db.add(sessione)
        self.db.commit()
        self.db.refresh(sessione)

        return sessione

    def update_sessione(
        self, sessione_id: int, update_data
    ) -> InterventoSessione:
        """Update work session"""
        from app.models.intervention import InterventoSessione

        sessione = (
            self.db.query(InterventoSessione)
            .filter_by(id=sessione_id, attivo=True)
            .first()
        )

        if not sessione:
            raise ValueError("Sessione non trovata")

        # Update fields
        update_dict = update_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(sessione, field, value)

        # Recalculate duration if times changed
        if "ora_inizio" in update_dict or "ora_fine" in update_dict:
            if sessione.ora_fine:
                inizio_minuti = sessione.ora_inizio.hour * 60 + sessione.ora_inizio.minute
                fine_minuti = sessione.ora_fine.hour * 60 + sessione.ora_fine.minute
                durata_minuti = fine_minuti - inizio_minuti
                if durata_minuti < 0:
                    durata_minuti += 24 * 60
                sessione.durata_minuti = durata_minuti

        sessione.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(sessione)

        return sessione

    def delete_sessione(self, sessione_id: int) -> None:
        """Soft delete work session"""
        from app.models.intervention import InterventoSessione

        sessione = (
            self.db.query(InterventoSessione)
            .filter_by(id=sessione_id, attivo=True)
            .first()
        )

        if not sessione:
            raise ValueError("Sessione non trovata")

        sessione.attivo = False
        sessione.updated_at = datetime.utcnow()
        self.db.commit()

    def calculate_total_hours(self, intervento_id: int) -> float:
        """Calculate total work hours for intervention"""
        from app.models.intervention import InterventoSessione
        from sqlalchemy import func

        result = (
            self.db.query(func.sum(InterventoSessione.durata_minuti))
            .filter(
                InterventoSessione.intervento_id == intervento_id,
                InterventoSessione.attivo == True,
            )
            .scalar()
        )

        return (result or 0) / 60.0  # Convert to hours

    # Righe Attività CRUD
    def get_righe(self, intervento_id: int) -> List[InterventoRiga]:
        """Get all activity rows for an intervention"""
        return (
            self.db.query(InterventoRiga)
            .filter(
                InterventoRiga.intervento_id == intervento_id,
                InterventoRiga.attivo == True,
            )
            .order_by(InterventoRiga.numero_riga)
            .all()
        )

    def update_riga(self, riga_id: int, update_data) -> InterventoRiga:
        """Update activity row"""
        riga = (
            self.db.query(InterventoRiga)
            .filter_by(id=riga_id, attivo=True)
            .first()
        )

        if not riga:
            raise ValueError("Riga non trovata")

        update_dict = update_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(riga, field, value)

        riga.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(riga)

        return riga

    def delete_riga(self, riga_id: int) -> None:
        """Soft delete activity row"""
        riga = (
            self.db.query(InterventoRiga)
            .filter_by(id=riga_id, attivo=True)
            .first()
        )

        if not riga:
            raise ValueError("Riga non trovata")

        riga.attivo = False
        riga.updated_at = datetime.utcnow()
        self.db.commit()

    def _generate_intervention_number(self) -> str:
        """Generate unique intervention number INT-YYYY-00001"""
        current_year = datetime.utcnow().year

        # Get last intervention number for current year
        last_intervento = (
            self.db.query(Intervento)
            .filter(Intervento.numero.like(f"INT-{current_year}-%"))
            .order_by(Intervento.numero.desc())
            .first()
        )

        if last_intervento:
            # Extract sequence number and increment
            last_num = int(last_intervento.numero.split("-")[-1])
            new_num = last_num + 1
        else:
            new_num = 1

        return f"INT-{current_year}-{new_num:05d}"
