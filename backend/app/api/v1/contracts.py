from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date
from decimal import Decimal
from app.database import get_db
from app.models.client import CacheContratti, CacheClienti, SLADefinizione
from app.api.v1.auth import get_current_user
from app.models.user import Tecnico
from pydantic import BaseModel

router = APIRouter()


class ContractCreate(BaseModel):
    codice_gestionale: str
    cliente_id: int
    descrizione: str
    tipo_contratto: Optional[str] = None
    data_inizio: date
    data_fine: Optional[date] = None
    attivo_gestionale: bool = True
    ore_incluse: Optional[float] = None
    ore_utilizzate: Optional[float] = 0.0
    importo_annuo: Optional[float] = None
    sla_id: Optional[int] = None


class ContractUpdate(BaseModel):
    descrizione: Optional[str] = None
    tipo_contratto: Optional[str] = None
    data_inizio: Optional[date] = None
    data_fine: Optional[date] = None
    attivo_gestionale: Optional[bool] = None
    ore_incluse: Optional[float] = None
    ore_utilizzate: Optional[float] = None
    importo_annuo: Optional[float] = None
    sla_id: Optional[int] = None


class ClienteMinimal(BaseModel):
    id: int
    codice_gestionale: str
    ragione_sociale: str

    class Config:
        from_attributes = True


class SLAMinimal(BaseModel):
    id: int
    nome: str
    descrizione: Optional[str] = None

    class Config:
        from_attributes = True


class ContractResponse(BaseModel):
    id: int
    codice_gestionale: str
    cliente_id: int
    cliente: Optional[ClienteMinimal] = None
    descrizione: str
    tipo_contratto: Optional[str] = None
    data_inizio: date
    data_fine: Optional[date] = None
    attivo_gestionale: bool
    ore_incluse: Optional[float] = None
    ore_utilizzate: Optional[float] = None
    importo_annuo: Optional[float] = None
    sla_id: Optional[int] = None
    sla: Optional[SLAMinimal] = None
    ultimo_sync: datetime
    attivo: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ContractListResponse(BaseModel):
    items: List[ContractResponse]
    total: int
    page: int
    limit: int


@router.get("", response_model=ContractListResponse)
async def get_contracts(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = None,
    cliente_id: Optional[int] = None,
    tipo_contratto: Optional[str] = None
,
    attivo_solo: Optional[bool] = None,
    scaduti: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: Tecnico = Depends(get_current_user)
):
    """Get list of contracts with filters"""
    query = db.query(CacheContratti)

    # Filters
    if search:
        search_filter = f"%{search}%"
        query = query.join(CacheClienti).filter(
            (CacheContratti.descrizione.ilike(search_filter)) |
            (CacheContratti.codice_gestionale.ilike(search_filter)) |
            (CacheClienti.ragione_sociale.ilike(search_filter))
        )

    if cliente_id is not None:
        query = query.filter(CacheContratti.cliente_id == cliente_id)

    if tipo_contratto:
        query = query.filter(CacheContratti.tipo_contratto == tipo_contratto)

    if attivo_solo:
        query = query.filter(
            CacheContratti.attivo == True,
            CacheContratti.attivo_gestionale == True
        )

    if scaduti is not None:
        today = date.today()
        if scaduti:
            query = query.filter(CacheContratti.data_fine < today)
        else:
            query = query.filter(
                (CacheContratti.data_fine >= today) | (CacheContratti.data_fine == None)
            )

    # Count total
    total = query.count()

    # Pagination
    offset = (page - 1) * limit
    items = query.order_by(
        CacheContratti.attivo_gestionale.desc(),
        CacheContratti.data_inizio.desc()
    ).offset(offset).limit(limit).all()

    return ContractListResponse(
        items=items,
        total=total,
        page=page,
        limit=limit
    )


@router.get("/{contract_id}", response_model=ContractResponse)
async def get_contract(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user: Tecnico = Depends(get_current_user)
):
    """Get contract by ID"""
    contract = db.query(CacheContratti).filter(CacheContratti.id == contract_id).first()
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    return contract


@router.post("", response_model=ContractResponse, status_code=status.HTTP_201_CREATED)
async def create_contract(
    data: ContractCreate,
    db: Session = Depends(get_db),
    current_user: Tecnico = Depends(get_current_user)
):
    """Create new contract"""
    # Check if codice_gestionale already exists
    existing = db.query(CacheContratti).filter(
        CacheContratti.codice_gestionale == data.codice_gestionale
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Contract code already exists")

    # Verify cliente exists
    cliente = db.query(CacheClienti).filter(CacheClienti.id == data.cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=400, detail="Client not found")

    # Verify SLA if provided
    if data.sla_id:
        sla = db.query(SLADefinizione).filter(SLADefinizione.id == data.sla_id).first()
        if not sla:
            raise HTTPException(status_code=400, detail="SLA not found")

    # Create contract
    contract = CacheContratti(
        codice_gestionale=data.codice_gestionale,
        cliente_id=data.cliente_id,
        descrizione=data.descrizione,
        tipo_contratto=data.tipo_contratto,
        data_inizio=data.data_inizio,
        data_fine=data.data_fine,
        attivo_gestionale=int(data.attivo_gestionale),
        ore_incluse=Decimal(str(data.ore_incluse)) if data.ore_incluse else None,
        ore_utilizzate=Decimal(str(data.ore_utilizzate)) if data.ore_utilizzate else Decimal('0.00'),
        importo_annuo=Decimal(str(data.importo_annuo)) if data.importo_annuo else None,
        sla_id=data.sla_id,
        ultimo_sync=datetime.utcnow(),
        attivo=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    db.add(contract)
    db.commit()
    db.refresh(contract)

    return contract


@router.put("/{contract_id}", response_model=ContractResponse)
async def update_contract(
    contract_id: int,
    data: ContractUpdate,
    db: Session = Depends(get_db),
    current_user: Tecnico = Depends(get_current_user)
):
    """Update contract"""
    contract = db.query(CacheContratti).filter(CacheContratti.id == contract_id).first()
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")

    # Update fields
    if data.descrizione is not None:
        contract.descrizione = data.descrizione
    if data.tipo_contratto is not None:
        contract.tipo_contratto = data.tipo_contratto
    if data.data_inizio is not None:
        contract.data_inizio = data.data_inizio
    if data.data_fine is not None:
        contract.data_fine = data.data_fine
    if data.attivo_gestionale is not None:
        contract.attivo_gestionale = int(data.attivo_gestionale)
    if data.ore_incluse is not None:
        contract.ore_incluse = Decimal(str(data.ore_incluse))
    if data.ore_utilizzate is not None:
        contract.ore_utilizzate = Decimal(str(data.ore_utilizzate))
    if data.importo_annuo is not None:
        contract.importo_annuo = Decimal(str(data.importo_annuo))
    if data.sla_id is not None:
        contract.sla_id = data.sla_id

    contract.updated_at = datetime.utcnow()
    contract.ultimo_sync = datetime.utcnow()

    db.commit()
    db.refresh(contract)

    return contract


@router.delete("/{contract_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contract(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user: Tecnico = Depends(get_current_user)
):
    """Delete (deactivate) contract"""
    contract = db.query(CacheContratti).filter(CacheContratti.id == contract_id).first()
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")

    # Soft delete
    contract.attivo = False
    contract.updated_at = datetime.utcnow()

    db.commit()
    return None


@router.get("/stats/by-client/{cliente_id}")
async def get_contract_stats_by_client(
    cliente_id: int,
    db: Session = Depends(get_db),
    current_user: Tecnico = Depends(get_current_user)
):
    """Get contract statistics for a specific client"""
    contracts = db.query(CacheContratti).filter(
        CacheContratti.cliente_id == cliente_id,
        CacheContratti.attivo == True
    ).all()

    total_contracts = len(contracts)
    active_contracts = len([c for c in contracts if c.attivo_gestionale])
    total_ore_incluse = sum([float(c.ore_incluse or 0) for c in contracts])
    total_ore_utilizzate = sum([float(c.ore_utilizzate or 0) for c in contracts])
    ore_residue = total_ore_incluse - total_ore_utilizzate

    return {
        "total_contracts": total_contracts,
        "active_contracts": active_contracts,
        "total_ore_incluse": total_ore_incluse,
        "total_ore_utilizzate": total_ore_utilizzate,
        "ore_residue": ore_residue,
        "percentuale_utilizzo": (total_ore_utilizzate / total_ore_incluse * 100) if total_ore_incluse > 0 else 0
    }
