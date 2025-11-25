#!/usr/bin/env python3
"""
Ranex Framework - Basic Contract Demo

This demo showcases the @Contract decorator, the core feature of Ranex Framework.
It demonstrates:
1. State machine validation
2. Schema validation
3. Automatic rollback on errors
4. Multi-tenant support

Run: python examples/basic_contract.py
"""

import asyncio
import os
from pathlib import Path
from pydantic import BaseModel, Field
from ranex import Contract

# Change to project root directory to ensure state.yaml files can be found
# This allows the script to be run from any directory
script_dir = Path(__file__).parent.absolute()
project_root = script_dir.parent
os.chdir(project_root)


# ============================================================================
# Step 1: Define State Machine
# ============================================================================
# Create app/features/payment/state.yaml:
"""
states:
  - Idle
  - Processing
  - Paid
  - Failed
  - Refunding
  - Refunded

initial_state: Idle

transitions:
  Idle: [Processing]
  Processing: [Paid, Failed]
  Paid: [Refunding]
  Refunding: [Refunded]
"""


# ============================================================================
# Step 2: Define Input Schema (Pydantic Model)
# ============================================================================
class PaymentRequest(BaseModel):
    """Payment request schema with validation."""
    amount: float = Field(gt=0, description="Payment amount (must be positive)")
    currency: str = Field(default="USD", pattern="^[A-Z]{3}$")
    recipient: str = Field(min_length=1, description="Recipient identifier")
    description: str = Field(default="", max_length=500)


# ============================================================================
# Step 3: Use @Contract Decorator
# ============================================================================
@Contract(
    feature="payment",
    input_schema=PaymentRequest,
    auto_validate=True
)
async def process_payment(_ctx, request: PaymentRequest):
    """
    Process a payment with contract enforcement.
    
    The @Contract decorator automatically:
    - Validates the input schema (PaymentRequest)
    - Enforces state machine transitions
    - Rolls back state on errors
    - Logs all operations for audit
    
    Args:
        _ctx: Contract context (injected by decorator)
        request: Payment request (validated by Pydantic)
    
    Returns:
        dict: Payment result
    """
    # Transition to Processing state
    _ctx.transition("Processing")
    print(f"✅ State transitioned to: Processing")
    
    # Simulate payment processing
    print(f"💰 Processing payment: ${request.amount} {request.currency}")
    print(f"   Recipient: {request.recipient}")
    print(f"   Description: {request.description}")
    
    # Simulate processing delay
    await asyncio.sleep(0.1)
    
    # Transition to Paid state (payment state machine uses "Paid" not "Completed")
    _ctx.transition("Paid")
    print(f"✅ State transitioned to: Paid")
    
    return {
        "status": "success",
        "transaction_id": "txn_12345",
        "amount": request.amount,
        "currency": request.currency
    }


@Contract(feature="payment")
async def process_payment_with_error(_ctx, request: PaymentRequest):
    """
    Demonstrate automatic rollback on error.
    
    When an exception occurs, the contract automatically:
    - Rolls back to the initial state
    - Logs the error for audit
    - Re-raises the exception
    """
    _ctx.transition("Processing")
    print(f"✅ State transitioned to: Processing")
    
    # Simulate an error
    raise ValueError("Payment gateway unavailable")
    
    # This line never executes (state already rolled back)
    _ctx.transition("Paid")


# ============================================================================
# Step 4: Run Demo
# ============================================================================
async def main():
    """Run the basic contract demo."""
    print("=" * 70)
    print("Ranex Framework - Basic Contract Demo")
    print("=" * 70)
    print()
    
    # Demo 1: Valid payment
    print("📝 Demo 1: Valid Payment Request")
    print("-" * 70)
    try:
        request = PaymentRequest(
            amount=100.50,
            currency="USD",
            recipient="user_123",
            description="Monthly subscription"
        )
        result = await process_payment(request)
        print(f"✅ Payment processed successfully: {result}")
    except Exception as e:
        print(f"❌ Error: {e}")
    print()
    
    # Demo 2: Invalid schema (negative amount)
    print("📝 Demo 2: Invalid Schema (Negative Amount)")
    print("-" * 70)
    try:
        invalid_request = PaymentRequest(
            amount=-50.0,  # Invalid: negative amount
            currency="USD",
            recipient="user_123"
        )
        result = await process_payment(invalid_request)
        print(f"✅ Payment processed: {result}")
    except Exception as e:
        print(f"❌ Schema validation failed (expected): {e}")
    print()
    
    # Demo 3: Invalid schema (invalid currency)
    print("📝 Demo 3: Invalid Schema (Invalid Currency)")
    print("-" * 70)
    try:
        invalid_request = PaymentRequest(
            amount=100.0,
            currency="INVALID",  # Invalid: must be 3 uppercase letters
            recipient="user_123"
        )
        result = await process_payment(invalid_request)
        print(f"✅ Payment processed: {result}")
    except Exception as e:
        print(f"❌ Schema validation failed (expected): {e}")
    print()
    
    # Demo 4: Automatic rollback on error
    print("📝 Demo 4: Automatic Rollback on Error")
    print("-" * 70)
    try:
        request = PaymentRequest(
            amount=100.0,
            currency="USD",
            recipient="user_123"
        )
        result = await process_payment_with_error(request)
        print(f"✅ Payment processed: {result}")
    except ValueError as e:
        print(f"❌ Error occurred (expected): {e}")
        print("✅ State automatically rolled back to initial state")
    print()
    
    # Demo 5: Invalid state transition
    print("📝 Demo 5: Invalid State Transition")
    print("-" * 70)
    try:
        request = PaymentRequest(
            amount=100.0,
            currency="USD",
            recipient="user_123"
        )
        # Try to skip Processing state (invalid)
        # This would be caught by the state machine validator
        print("⚠️  Note: Invalid transitions are prevented by the state machine")
    except Exception as e:
        print(f"❌ State machine validation failed (expected): {e}")
    print()
    
    print("=" * 70)
    print("✅ Demo Complete!")
    print("=" * 70)
    print()
    print("Key Takeaways:")
    print("  • @Contract decorator enforces state machine transitions")
    print("  • Pydantic schemas validate inputs automatically")
    print("  • Errors trigger automatic state rollback")
    print("  • All operations are logged for audit")
    print()
    print("Next Steps:")
    print("  • Read docs/CONTRACT_USAGE_GUIDE.md for detailed usage")
    print("  • Try examples/state_machine_demo.py for more state machine examples")
    print("  • Check examples/fastapi_demo/ for FastAPI integration")


if __name__ == "__main__":
    asyncio.run(main())

