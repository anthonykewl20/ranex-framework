from app.features.payment import models  # <--- ILLEGAL DIRECT ACCESS
from fastapi import APIRouter, Depends, HTTPException, Request

from sqlalchemy.orm import Session
from app.commons.database import get_db
from . import service
from app.commons.contract_middleware import get_tenant_id
from fastapi import Request  # Import Request type for type hints

router = APIRouter()


@router.post("/pay")
async def pay(transaction_id: str, amount: float, request: Request, db: Session = Depends(get_db)):
    try:
        # Get tenant_id from middleware if available
        tenant_id = get_tenant_id(request)
        return await service.process_payment(transaction_id=transaction_id, amount=amount, db=db, tenant_id=tenant_id)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/refund")
async def refund(transaction_id: str, amount: float, request: Request, db: Session = Depends(get_db)):
    try:
        # Get tenant_id from middleware if available
        tenant_id = get_tenant_id(request)
        return await service.process_refund(payment_id=transaction_id, amount=amount, tenant_id=tenant_id)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"RANEX BLOCK: {str(exc)}")
