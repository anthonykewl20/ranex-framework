#!/usr/bin/env python3
"""
Ranex Framework - Intent Airlock Demo

This demo showcases intent validation and ambiguity detection.
It demonstrates:
1. Ambiguity detection
2. Clarifying questions
3. Intent validation
4. Feature manifest validation

Run: python examples/intent_airlock_demo.py
"""

import json
from ranex_core import IntentAirlock


def demo_intent_airlock():
    """Demonstrate intent airlock capabilities."""
    print("=" * 70)
    print("Ranex Framework - Intent Airlock Demo")
    print("=" * 70)
    print()
    
    airlock = IntentAirlock()
    print("✅ Intent airlock initialized")
    print()
    
    # Demo 1: Ambiguous intent (rejected)
    print("📝 Demo 1: Ambiguous Intent (Rejected)")
    print("-" * 70)
    
    ambiguous_manifest = {
        "feature_name": "auth",
        "description": "Add auth",  # Too vague
        "primary_actor": None,  # Missing
        "data_impact": None,  # Missing
    }
    
    print("Testing ambiguous manifest:")
    print(f"  Feature: {ambiguous_manifest['feature_name']}")
    print(f"  Description: {ambiguous_manifest['description']}")
    print()
    
    try:
        result_json = airlock.validate_manifest(json.dumps(ambiguous_manifest))
        result = json.loads(result_json)
        
        if result["status"] == "REJECTED":
            print("  ✅ Correctly rejected (ambiguous)")
            print(f"  Reason: {result['reason']}")
            print("  Questions to ask:")
            for question in result["questions"]:
                print(f"    • {question}")
        else:
            print("  ⚠️  Unexpectedly accepted")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    print()
    
    # Demo 2: Clear intent (accepted)
    print("📝 Demo 2: Clear Intent (Accepted)")
    print("-" * 70)
    
    clear_manifest = {
        "feature_name": "user_authentication",
        "description": "Implement user authentication system with email/password login, JWT tokens, and password reset functionality",
        "primary_actor": "end_user",
        "complexity": "medium",
        "data_impact": "handles passwords and personal information",
    }
    
    print("Testing clear manifest:")
    print(f"  Feature: {clear_manifest['feature_name']}")
    print(f"  Description: {clear_manifest['description'][:60]}...")
    print(f"  Primary Actor: {clear_manifest['primary_actor']}")
    print(f"  Data Impact: {clear_manifest['data_impact']}")
    print()
    
    try:
        result_json = airlock.validate_manifest(json.dumps(clear_manifest))
        result = json.loads(result_json)
        
        if result["status"] == "ACCEPTED":
            print("  ✅ Correctly accepted (clear intent)")
            print(f"  Message: {result['message']}")
        else:
            print("  ⚠️  Unexpectedly rejected")
            print(f"  Reason: {result.get('reason', 'Unknown')}")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    print()
    
    # Demo 3: Missing fields
    print("📝 Demo 3: Missing Required Fields")
    print("-" * 70)
    
    incomplete_manifests = [
        {
            "name": "Missing primary_actor",
            "manifest": {
                "feature_name": "payment",
                "description": "Process payments securely with multiple payment gateways",
                "primary_actor": None,
                "data_impact": "handles credit card information",
            }
        },
        {
            "name": "Missing data_impact",
            "manifest": {
                "feature_name": "notifications",
                "description": "Send email and SMS notifications to users",
                "primary_actor": "system",
                "data_impact": None,
            }
        },
        {
            "name": "Vague description",
            "manifest": {
                "feature_name": "search",
                "description": "Search",  # Too short
                "primary_actor": "end_user",
                "data_impact": "no sensitive data",
            }
        },
    ]
    
    for test_case in incomplete_manifests:
        print(f"Testing: {test_case['name']}")
        try:
            result_json = airlock.validate_manifest(json.dumps(test_case["manifest"]))
            result = json.loads(result_json)
            
            if result["status"] == "REJECTED":
                print(f"  ✅ Correctly rejected")
                print(f"  Questions: {len(result['questions'])}")
            else:
                print(f"  ⚠️  Unexpectedly accepted")
        except Exception as e:
            print(f"  ❌ Error: {e}")
        print()
    
    # Demo 4: Benefits
    print("📝 Demo 4: Benefits of Intent Airlock")
    print("-" * 70)
    print("Intent airlock prevents:")
    print("  • Ambiguous requirements")
    print("  • Premature implementation")
    print("  • Misunderstood features")
    print("  • Security oversights")
    print()
    print("Ensures:")
    print("  • Clear feature definitions")
    print("  • Security considerations")
    print("  • User context understanding")
    print("  • Complete requirements")
    print()
    
    # Demo 5: Integration example
    print("📝 Demo 5: Integration Example")
    print("-" * 70)
    print("""
# Example: AI code generation workflow

from ranex_core import IntentAirlock
import json

airlock = IntentAirlock()

def process_feature_request(user_request: str):
    # Create manifest from user request
    manifest = {
        "feature_name": extract_feature_name(user_request),
        "description": user_request,
        "primary_actor": None,  # Need to ask
        "data_impact": None,  # Need to ask
    }
    
    # Validate intent
    result_json = airlock.validate_manifest(json.dumps(manifest))
    result = json.loads(result_json)
    
    if result["status"] == "REJECTED":
        # Ask clarifying questions
        print("❌ Request is ambiguous. Please clarify:")
        for question in result["questions"]:
            print(f"  • {question}")
        return None
    else:
        # Proceed with implementation
        print("✅ Intent is clear. Proceeding...")
        return result["manifest"]
""")
    print()
    
    print("=" * 70)
    print("✅ Demo Complete!")
    print("=" * 70)
    print()
    print("Key Takeaways:")
    print("  • Intent airlock prevents ambiguous requests")
    print("  • Ensures complete feature definitions")
    print("  • Prompts for missing information")
    print("  • Validates security considerations")
    print()
    print("Next Steps:")
    print("  • Try examples/workflow_management_demo.py for workflow management")
    print("  • Use with AI code generation")
    print("  • Integrate into feature request process")


if __name__ == "__main__":
    demo_intent_airlock()

