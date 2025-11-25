"""
Unit tests for @Contract decorator.

Run with: pytest tests/test_contract.py
Or: python -m pytest tests/test_contract.py
"""
import pytest
import asyncio
from ranex import Contract
from pydantic import BaseModel, Field


class PaymentRequest(BaseModel):
    """Test payment request schema."""
    amount: float = Field(gt=0)
    currency: str = Field(default="USD")


class TestContract:
    """Test @Contract decorator."""
    
    @pytest.mark.asyncio
    async def test_contract_decorator_basic(self):
        """Test basic @Contract decorator functionality."""
        @Contract(feature="payment")
        async def process_payment(_ctx, amount: float):
            _ctx.transition("Processing")
            _ctx.transition("Paid")
            return {"status": "success", "amount": amount}
        
        result = await process_payment(100.0)
        assert result["status"] == "success"
        assert result["amount"] == 100.0
    
    @pytest.mark.asyncio
    async def test_contract_with_schema(self):
        """Test @Contract with Pydantic schema (schema validation may be disabled)."""
        @Contract(feature="payment", input_schema=PaymentRequest)
        async def process_payment(_ctx, request: PaymentRequest):
            _ctx.transition("Processing")
            _ctx.transition("Paid")
            return {"status": "success", "amount": request.amount}
        
        request = PaymentRequest(amount=50.0, currency="USD")
        result = await process_payment(request)
        assert result["status"] == "success"
        assert result["amount"] == 50.0
    
    @pytest.mark.asyncio
    async def test_contract_state_transitions(self):
        """Test that contract enforces state transitions."""
        @Contract(feature="payment")
        async def process_payment(_ctx, amount: float):
            _ctx.transition("Processing")
            # Try invalid transition - should raise error
            _ctx.transition("Refunded")  # Cannot skip Paid - should raise ValueError
        
        # The invalid transition should raise ValueError
        with pytest.raises(ValueError, match="Illegal transition"):
            await process_payment(100.0)
    
    @pytest.mark.asyncio
    async def test_contract_error_handling(self):
        """Test that errors in contract functions are handled."""
        @Contract(feature="payment")
        async def failing_payment(_ctx, amount: float):
            _ctx.transition("Processing")
            raise ValueError("Payment gateway error")
        
        with pytest.raises(ValueError, match="Payment gateway error"):
            await failing_payment(100.0)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

