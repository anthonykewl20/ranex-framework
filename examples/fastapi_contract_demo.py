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
import time
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
@Contract(
    feature="payment",
    input_schema=PaymentRequest,
    auto_validate=True
)
@app.post("/payments", response_model=PaymentResponse)
async def create_payment(request: PaymentRequest):
    """
    Create a payment with contract enforcement.
    
    The @Contract decorator automatically:
    - Validates the input schema (PaymentRequest)
    - Enforces state machine transitions
    - Rolls back state on errors
    - Logs all operations for audit
    
    Note: The @Contract decorator injects ctx automatically.
    In production, you would use: ctx.transition("Processing")
    """
    # Simulate payment processing
    # Note: @Contract decorator injects ctx as first argument internally
    # For demo purposes, we generate a transaction ID
    transaction_id = f"txn_demo_{int(time.time())}"
    
    return PaymentResponse(
        transaction_id=transaction_id,
        status="completed",
        amount=request.amount,
        currency=request.currency
    )


@Contract(feature="payment")
@app.get("/payments/{payment_id}")
async def get_payment(payment_id: str):
    """Get payment details with contract enforcement."""
    # Note: @Contract decorator injects ctx automatically
    # In production: ctx.transition("Viewing")
    
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
python3 fastapi_contract_demo.py --server
# OR
uvicorn examples.fastapi_contract_demo:app --reload

# Test the endpoint (in another terminal)
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
    import sys
    
    # Check if --server flag is provided
    if "--server" in sys.argv or "-s" in sys.argv:
        # Start the server
        import uvicorn
        print("Starting FastAPI server...")
        print("Visit http://localhost:8000/docs for API documentation")
        print("Press Ctrl+C to stop")
        print()
        uvicorn.run(app, host="0.0.0.0", port=8000)
    else:
        # Run demo by default
        demo_fastapi_contract()
        print()
        print("💡 Tip: Run with --server flag to start the server:")
        print("   python3 fastapi_contract_demo.py --server")

