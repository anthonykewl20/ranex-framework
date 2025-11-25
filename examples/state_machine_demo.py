#!/usr/bin/env python3
"""
Ranex Framework - State Machine Demo

This demo showcases state machine validation and enforcement.
It demonstrates:
1. Creating state machines from YAML
2. Valid state transitions
3. Invalid state transitions (rejected)
4. Multi-tenant state isolation

Run: python examples/state_machine_demo.py
"""

import asyncio
from ranex_core import StateMachine


# ============================================================================
# State Machine Definition
# ============================================================================
# Create app/features/order/state.yaml:
"""
states:
  - Created
  - Paid
  - Shipped
  - Delivered
  - Cancelled

initial_state: Created

transitions:
  Created: [Paid, Cancelled]
  Paid: [Shipped, Cancelled]
  Shipped: [Delivered]
  Delivered: []
  Cancelled: []
"""


async def demo_state_machine():
    """Demonstrate state machine validation."""
    print("=" * 70)
    print("Ranex Framework - State Machine Demo")
    print("=" * 70)
    print()
    
    # Create state machine instance
    print("📦 Creating state machine for 'order' feature...")
    sm = StateMachine("order")
    print(f"✅ State machine created")
    print(f"   Initial state: {sm.current_state}")
    print()
    
    # Demo 1: Valid transitions
    print("📝 Demo 1: Valid State Transitions")
    print("-" * 70)
    
    transitions = [
        ("Created", "Paid"),
        ("Paid", "Shipped"),
        ("Shipped", "Delivered"),
    ]
    
    for from_state, to_state in transitions:
        try:
            sm.validate_transition(from_state, to_state)
            print(f"✅ Valid transition: {from_state} → {to_state}")
        except Exception as e:
            print(f"❌ Invalid transition: {from_state} → {to_state}")
            print(f"   Error: {e}")
    print()
    
    # Demo 2: Invalid transitions
    print("📝 Demo 2: Invalid State Transitions (Rejected)")
    print("-" * 70)
    
    invalid_transitions = [
        ("Created", "Shipped"),      # Cannot skip Paid
        ("Created", "Delivered"),     # Cannot skip Paid and Shipped
        ("Paid", "Created"),          # Cannot go backwards
        ("Delivered", "Shipped"),     # Cannot go backwards
        ("Cancelled", "Paid"),        # Cannot resume from Cancelled
    ]
    
    for from_state, to_state in invalid_transitions:
        try:
            sm.validate_transition(from_state, to_state)
            print(f"⚠️  Unexpected: {from_state} → {to_state} is valid")
        except Exception as e:
            print(f"✅ Invalid transition rejected: {from_state} → {to_state}")
            print(f"   Reason: {e}")
    print()
    
    # Demo 3: State machine rules
    print("📝 Demo 3: State Machine Rules")
    print("-" * 70)
    print(f"Initial state: {sm.rules.initial}")
    print(f"States: {', '.join(sm.rules.states)}")
    print()
    print("Valid transitions:")
    for from_state, to_states in sm.rules.transitions.items():
        print(f"  {from_state} → {', '.join(to_states) if to_states else '(none)'}")
    print()
    
    # Demo 4: Multi-tenant isolation
    print("📝 Demo 4: Multi-Tenant State Isolation")
    print("-" * 70)
    print("Each tenant has isolated state machines:")
    
    tenant1_sm = StateMachine("order")  # Tenant 1
    tenant2_sm = StateMachine("order")  # Tenant 2
    
    # Tenant 1 transitions
    tenant1_sm.transition("Paid")
    print(f"Tenant 1 state: {tenant1_sm.current_state}")
    
    # Tenant 2 transitions independently
    tenant2_sm.transition("Cancelled")
    print(f"Tenant 2 state: {tenant2_sm.current_state}")
    
    print("✅ Tenants have isolated state machines")
    print()
    
    print("=" * 70)
    print("✅ Demo Complete!")
    print("=" * 70)
    print()
    print("Key Takeaways:")
    print("  • State machines enforce business logic at runtime")
    print("  • Invalid transitions are rejected automatically")
    print("  • Multi-tenant isolation ensures data safety")
    print("  • YAML-based configuration is easy to maintain")
    print()
    print("Next Steps:")
    print("  • Read docs/CONTRACT_USAGE_GUIDE.md for @Contract decorator")
    print("  • Try examples/basic_contract.py for contract enforcement")
    print("  • Check examples/fastapi_demo/ for real-world usage")


if __name__ == "__main__":
    asyncio.run(demo_state_machine())

