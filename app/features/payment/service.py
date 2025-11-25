# app/features/payment/service.py
from ranex import Contract
from typing import Optional
from sqlalchemy.orm import Session


# Mocking an external payment provider for the prototype
class Stripe:
    async def refund(self, id, amount):
        return type('obj', (object,), {'success': True})()
    
    async def charge(self, id, amount):
        return type('obj', (object,), {'success': True})()


stripe = Stripe()


@Contract("payment", tenant_id=None)  # tenant_id will be extracted from request if None
async def process_payment(_ctx, transaction_id: str, amount: float, db: Session, tenant_id: Optional[str] = None):
    """
    Process a payment with contract validation and multi-tenant support.
    
    The @Contract decorator will use tenant_id for state isolation if provided.
    If tenant_id is None, it will try to get it from FastAPI request state (via ContractMiddleware).
    """
    # Ranex validates this transition via Rust
    _ctx.transition("Processing")
    
    # Business logic
    result = await stripe.charge(transaction_id, amount)
    
    if result.success:
        _ctx.transition("Paid")  # ✅ Valid
        return {"status": "success", "transaction_id": transaction_id, "amount": amount}
    else:
        _ctx.transition("Failed")  # ✅ Valid
        return {"status": "failed", "transaction_id": transaction_id}


@Contract("payment", tenant_id=None)  # tenant_id will be extracted from request if None
async def process_refund(_ctx, payment_id: str, amount: float, tenant_id: Optional[str] = None):
    """
    Process a refund with contract validation and multi-tenant support.
    
    The @Contract decorator will use tenant_id for state isolation if provided.
    If tenant_id is None, it will try to get it from FastAPI request state (via ContractMiddleware).
    """
    # Ranex validates this transition via Rust
    # If current state isn't 'Paid', this crashes (as it should)
    _ctx.transition("Refunding")
    
    # Business logic
    result = await stripe.refund(payment_id, amount)
    
    if result.success:
        _ctx.transition("Refunded")  # ✅ Valid
    else:
        _ctx.transition("Failed")     # ✅ Valid (assuming Failed is reachable)
    
    return result
