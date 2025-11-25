#!/usr/bin/env python3
"""
Ranex Framework - Schema Validation Demo

This demo showcases Pydantic schema validation integration.
It demonstrates:
1. Schema registration
2. Validation against JSON Schema
3. Field-level error reporting
4. Nested schema validation

Run: python examples/schema_validation_demo.py
"""

from pydantic import BaseModel, Field

# SchemaValidator may not be available in pre-release
try:
    from ranex_core import SchemaValidator
    SCHEMA_VALIDATOR_AVAILABLE = True
except ImportError:
    print("⚠️  SchemaValidator not available in this build.")
    print("   Schema validation is optional in pre-release.")
    SCHEMA_VALIDATOR_AVAILABLE = False
    SchemaValidator = None


class UserCreate(BaseModel):
    """User creation schema."""
    email: str = Field(..., pattern=r'^[^@]+@[^@]+\.[^@]+$')
    name: str = Field(..., min_length=1, max_length=100)
    age: int = Field(..., ge=0, le=150)


class PaymentRequest(BaseModel):
    """Payment request schema."""
    amount: float = Field(..., gt=0)
    currency: str = Field(default="USD", pattern=r'^[A-Z]{3}$')
    description: str = Field(default="", max_length=500)


def demo_schema_validation():
    """Demonstrate schema validation capabilities."""
    print("=" * 70)
    print("Ranex Framework - Schema Validation Demo")
    print("=" * 70)
    print()
    
    if not SCHEMA_VALIDATOR_AVAILABLE or SchemaValidator is None:
        print("⚠️  SchemaValidator not available in this pre-release build.")
        print("   This feature is optional and may not be included.")
        print("   Schema validation is still available via @Contract decorator.")
        print("   See examples/basic_contract.py for contract-based validation.")
        return
    
    validator = SchemaValidator()
    print("✅ Schema validator initialized")
    print()
    
    # Demo 1: Register schemas
    print("📝 Demo 1: Register Schemas")
    print("-" * 70)
    
    try:
        # Register UserCreate schema
        user_schema = UserCreate.model_json_schema()
        validator.register_schema("UserCreate", user_schema)
        print("✅ Registered schema: UserCreate")
        
        # Register PaymentRequest schema
        payment_schema = PaymentRequest.model_json_schema()
        validator.register_schema("PaymentRequest", payment_schema)
        print("✅ Registered schema: PaymentRequest")
    except Exception as e:
        print(f"⚠️  Schema registration error: {e}")
    print()
    
    # Demo 2: Valid data
    print("📝 Demo 2: Valid Data Validation")
    print("-" * 70)
    
    valid_user = {
        "email": "user@example.com",
        "name": "John Doe",
        "age": 30
    }
    
    try:
        result = validator.validate("UserCreate", valid_user)
        if result.valid:
            print(f"✅ Validation passed")
            print(f"   Sanitized value: {result.sanitized_value[:100]}...")
        else:
            print(f"❌ Validation failed")
            print(f"   Errors: {result.errors}")
    except Exception as e:
        print(f"⚠️  Validation error: {e}")
    print()
    
    # Demo 3: Invalid data
    print("📝 Demo 3: Invalid Data Validation")
    print("-" * 70)
    
    invalid_cases = [
        {
            "data": {"email": "invalid-email", "name": "John", "age": 30},
            "description": "Invalid email format"
        },
        {
            "data": {"email": "user@example.com", "name": "", "age": 30},
            "description": "Empty name"
        },
        {
            "data": {"email": "user@example.com", "name": "John", "age": -5},
            "description": "Negative age"
        },
        {
            "data": {"email": "user@example.com", "name": "John", "age": 200},
            "description": "Age too high"
        },
    ]
    
    for case in invalid_cases:
        print(f"Testing: {case['description']}")
        try:
            result = validator.validate("UserCreate", case["data"])
            if not result.valid:
                print(f"  ✅ Correctly rejected")
                print(f"     Errors: {result.errors}")
                if result.field_errors:
                    print(f"     Field errors: {result.field_errors}")
            else:
                print(f"  ⚠️  Unexpectedly accepted")
        except Exception as e:
            print(f"  ⚠️  Validation error: {e}")
        print()
    
    # Demo 4: Payment validation
    print("📝 Demo 4: Payment Schema Validation")
    print("-" * 70)
    
    payment_cases = [
        {"amount": 100.50, "currency": "USD", "description": "Test payment"},
        {"amount": -50.0, "currency": "USD"},  # Invalid: negative amount
        {"amount": 100.0, "currency": "INVALID"},  # Invalid: currency format
        {"amount": 100.0, "currency": "USD", "description": "A" * 600},  # Invalid: description too long
    ]
    
    for i, payment in enumerate(payment_cases, 1):
        print(f"Payment {i}:")
        try:
            result = validator.validate("PaymentRequest", payment)
            if result.valid:
                print(f"  ✅ Valid payment")
            else:
                print(f"  ❌ Invalid payment")
                print(f"     Errors: {result.errors}")
        except Exception as e:
            print(f"  ⚠️  Validation error: {e}")
        print()
    
    # Demo 5: Benefits
    print("📝 Demo 5: Benefits of Schema Validation")
    print("-" * 70)
    print("Schema validation provides:")
    print("  • Type safety at runtime")
    print("  • Field-level error reporting")
    print("  • Pydantic integration")
    print("  • Fast validation (Rust-based)")
    print("  • Sanitized logging")
    print()
    print("Use cases:")
    print("  • API request validation")
    print("  • Database input validation")
    print("  • Configuration validation")
    print("  • Data transformation validation")
    print()
    
    print("=" * 70)
    print("✅ Demo Complete!")
    print("=" * 70)
    print()
    print("Key Takeaways:")
    print("  • Schema validation ensures data integrity")
    print("  • Field-level errors help debugging")
    print("  • Pydantic integration for Python developers")
    print("  • Fast Rust-based validation")
    print()
    print("Next Steps:")
    print("  • Try examples/ffi_validation_demo.py for FFI validation")
    print("  • Use with @Contract decorator")
    print("  • Integrate into API endpoints")


if __name__ == "__main__":
    demo_schema_validation()

