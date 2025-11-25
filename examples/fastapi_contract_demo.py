#!/usr/bin/env python3
"""
Ranex Framework - FastAPI + @Contract Integration Demo

This demo showcases FastAPI integration with Ranex @Contract decorator.
It demonstrates:
1. FastAPI route decoration with @Contract
2. State machine integration
3. Schema validation
4. Error handling

Run: python examples/fastapi_contract_demo.py
"""

import os
from pathlib import Path
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from ranex import Contract

# Change to project root directory to ensure state.yaml files can be found
# This allows the script to be run from any directory
script_dir = Path(__file__).parent.absolute()
project_root = script_dir.parent
os.chdir(project_root)

app = FastAPI(title="Ranex FastAPI Contract Demo")


# Define schemas
class PaymentRequest(BaseModel):
    """Payment request schema."""
    amount: float = Field(..., gt=0, description="Payment amount (must be positive)")
    currency: str = Field(default="USD", pattern=r'^[A-Z]{3}$')
    recipient: str = Field(..., min_length=1)


class PaymentResponse(BaseModel):
    """Payment response schema."""
    transaction_id: str
    status: str
    amount: float
    currency: str


# FastAPI route with @Contract decorator
@app.post("/payments", response_model=PaymentResponse)
@Contract(
    feature="payment",
    input_schema=PaymentRequest,
    auto_validate=True
)
async def create_payment(_ctx, request: PaymentRequest):
    """
    Create a payment with contract enforcement.
    
    The @Contract decorator automatically:
    - Validates the input schema (PaymentRequest)
    - Enforces state machine transitions
    - Rolls back state on errors
    - Logs all operations for audit
    """
    # Transition to Processing state
    _ctx.transition("Processing")
    
    # Simulate payment processing
    transaction_id = f"txn_{_ctx.request_id}"
    
    # Transition to Completed state
    _ctx.transition("Completed")
    
    return PaymentResponse(
        transaction_id=transaction_id,
        status="completed",
        amount=request.amount,
        currency=request.currency
    )


@app.get("/payments/{payment_id}")
@Contract(feature="payment")
async def get_payment(_ctx, payment_id: str):
    """Get payment details with contract enforcement."""
    _ctx.transition("Viewing")
    
    # Simulate fetching payment
    return {
        "payment_id": payment_id,
        "status": "completed",
        "amount": 100.0,
        "currency": "USD"
    }


def demo_fastapi_contract():
    """Demonstrate FastAPI + Contract integration."""
    print("=" * 70)
    print("Ranex Framework - FastAPI + @Contract Integration Demo")
    print("=" * 70)
    print()
    
    print("✅ FastAPI application created with @Contract integration")
    print()
    
    print("📝 Key Features:")
    print("-" * 70)
    print("1. Route Decoration:")
    print("   @app.post('/payments')")
    print("   @Contract(feature='payment', input_schema=PaymentRequest)")
    print("   async def create_payment(_ctx, request: PaymentRequest):")
    print()
    print("2. Automatic Validation:")
    print("   • Input schema validation (Pydantic)")
    print("   • State machine enforcement")
    print("   • Error handling and rollback")
    print()
    print("3. State Management:")
    print("   • Automatic state transitions")
    print("   • Multi-tenant isolation")
    print("   • Audit trail")
    print()
    
    print("📝 Example Usage:")
    print("-" * 70)
    print("""
# Start the server
uvicorn examples.fastapi_contract_demo:app --reload

# Test the endpoint
curl -X POST "http://localhost:8000/payments" \\
  -H "Content-Type: application/json" \\
  -d '{
    "amount": 100.50,
    "currency": "USD",
    "recipient": "user_123"
  }'

# Response:
{
  "transaction_id": "txn_...",
  "status": "completed",
  "amount": 100.5,
  "currency": "USD"
}
""")
    print()
    
    print("📝 Benefits:")
    print("-" * 70)
    print("  • Type-safe API endpoints")
    print("  • Automatic input validation")
    print("  • State machine enforcement")
    print("  • Multi-tenant support")
    print("  • Audit trail for all operations")
    print("  • Error handling and rollback")
    print()
    
    print("=" * 70)
    print("✅ Demo Complete!")
    print("=" * 70)
    print()
    print("Next Steps:")
    print("  • Try examples/fastapi_middleware_demo.py for middleware")
    print("  • See examples/fastapi_demo/ for complete application")
    print("  • Read docs/CONTRACT_USAGE_GUIDE.md for details")


if __name__ == "__main__":
    import uvicorn
    print("Starting FastAPI server...")
    print("Visit http://localhost:8000/docs for API documentation")
    print("Press Ctrl+C to stop")
    print()
    uvicorn.run(app, host="0.0.0.0", port=8000)

