"""
Unit tests for StateMachine functionality.

Run with: pytest tests/test_state_machine.py
Or: python -m pytest tests/test_state_machine.py
"""
import pytest
from ranex_core import StateMachine


class TestStateMachine:
    """Test StateMachine class."""
    
    def test_create_state_machine(self):
        """Test creating a state machine."""
        sm = StateMachine("payment")
        assert sm.current_state == "Idle"
        assert sm.rules.initial == "Idle"
    
    def test_valid_transition(self):
        """Test valid state transition."""
        sm = StateMachine("payment")
        sm.transition("Processing")
        assert sm.current_state == "Processing"
    
    def test_invalid_transition_raises_error(self):
        """Test invalid state transition raises ValueError."""
        sm = StateMachine("payment")
        with pytest.raises(ValueError, match="Illegal transition"):
            sm.transition("Paid")  # Cannot skip Processing
    
    def test_state_machine_rules(self):
        """Test state machine rules are accessible."""
        sm = StateMachine("payment")
        assert sm.rules.initial == "Idle"
        assert "Processing" in sm.rules.states
        assert "Paid" in sm.rules.states
        assert "Failed" in sm.rules.states
    
    def test_complete_payment_flow(self):
        """Test complete valid payment flow."""
        sm = StateMachine("payment")
        assert sm.current_state == "Idle"
        
        sm.transition("Processing")
        assert sm.current_state == "Processing"
        
        sm.transition("Paid")
        assert sm.current_state == "Paid"
        
        sm.transition("Refunding")
        assert sm.current_state == "Refunding"
        
        sm.transition("Refunded")
        assert sm.current_state == "Refunded"
    
    def test_failed_payment_flow(self):
        """Test payment failure flow."""
        sm = StateMachine("payment")
        sm.transition("Processing")
        sm.transition("Failed")
        assert sm.current_state == "Failed"
    
    def test_cannot_go_backwards(self):
        """Test that backwards transitions are not allowed."""
        sm = StateMachine("payment")
        sm.transition("Processing")
        
        with pytest.raises(ValueError):
            sm.transition("Idle")  # Cannot go backwards


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

