#!/usr/bin/env python3
"""
Ranex Framework - FFI Validation Demo

This demo showcases FFI (Foreign Function Interface) validation.
It demonstrates:
1. Type validation at Rust/Python boundary
2. Parameter validation
3. Return type validation
4. Performance-optimized validation

Run: python examples/ffi_validation_demo.py
"""

from ranex_core import FFIValidator


def demo_ffi_validation():
    """Demonstrate FFI validation capabilities."""
    print("=" * 70)
    print("Ranex Framework - FFI Validation Demo")
    print("=" * 70)
    print()
    
    validator = FFIValidator()
    print("✅ FFI validator initialized")
    print()
    
    # Demo 1: Type validation
    print("📝 Demo 1: Type Validation")
    print("-" * 70)
    
    test_cases = [
        ("hello", "str", True),
        (123, "int", True),
        (123, "str", False),
        (45.67, "float", True),
        (True, "bool", True),
        ({"key": "value"}, "dict", True),
        ([1, 2, 3], "list", True),
    ]
    
    print("Testing type validation:")
    for value, expected_type, should_pass in test_cases:
        try:
            result = validator.validate_type(value, expected_type)
            status = "✅" if result.valid == should_pass else "❌"
            print(f"  {status} {type(value).__name__} as {expected_type}: {result.valid}")
            if not result.valid and result.error:
                print(f"     Error: {result.error}")
        except Exception as e:
            print(f"  ⚠️  Error validating {value} as {expected_type}: {e}")
    print()
    
    # Demo 2: Positive integer validation
    print("📝 Demo 2: Positive Integer Validation")
    print("-" * 70)
    
    integer_cases = [
        (10, True),
        (0, False),  # Zero is not positive
        (-5, False),  # Negative is not positive
        (100, True),
    ]
    
    print("Testing positive integer validation:")
    for value, should_pass in integer_cases:
        try:
            result = validator.validate_positive_int(value)
            status = "✅" if result.valid == should_pass else "❌"
            print(f"  {status} {value}: {result.valid}")
            if not result.valid and result.error:
                print(f"     Error: {result.error}")
        except Exception as e:
            print(f"  ⚠️  Error validating {value}: {e}")
    print()
    
    # Demo 3: Performance
    print("📝 Demo 3: Performance Characteristics")
    print("-" * 70)
    print("FFI validation is optimized for performance:")
    print("  • <100ns per validation (target)")
    print("  • Zero Python overhead")
    print("  • All validation in Rust")
    print("  • Fast type checking")
    print()
    print("Use cases:")
    print("  • Pre-execution validation")
    print("  • Function parameter validation")
    print("  • Return value validation")
    print("  • High-frequency validation")
    print()
    
    # Demo 4: Integration example
    print("📝 Demo 4: Integration Example")
    print("-" * 70)
    print("""
# Example: Validate function parameters

from ranex_core import FFIValidator

validator = FFIValidator()

def process_payment(amount: float, currency: str):
    # Validate before processing
    amount_result = validator.validate_type(amount, "float")
    if not amount_result.valid:
        raise ValueError(f"Invalid amount: {amount_result.error}")
    
    currency_result = validator.validate_type(currency, "str")
    if not currency_result.valid:
        raise ValueError(f"Invalid currency: {currency_result.error}")
    
    # Process payment...
    return {"status": "success"}

# Usage
process_payment(100.50, "USD")  # ✅ Valid
process_payment("invalid", "USD")  # ❌ Invalid (amount not float)
""")
    print()
    
    # Demo 5: Benefits
    print("📝 Demo 5: Benefits of FFI Validation")
    print("-" * 70)
    print("FFI validation provides:")
    print("  • Type safety at Rust/Python boundary")
    print("  • Performance-optimized validation")
    print("  • Pre-execution error detection")
    print("  • Sanitized logging")
    print()
    print("Why it matters:")
    print("  • Prevents type errors at runtime")
    print("  • Fast enough for high-frequency calls")
    print("  • No Python overhead")
    print("  • Works with @Contract decorator")
    print()
    
    print("=" * 70)
    print("✅ Demo Complete!")
    print("=" * 70)
    print()
    print("Key Takeaways:")
    print("  • FFI validation ensures type safety")
    print("  • Optimized for performance (<100ns)")
    print("  • Pre-execution validation")
    print("  • Zero Python overhead")
    print()
    print("Next Steps:")
    print("  • Try examples/schema_validation_demo.py for schema validation")
    print("  • Use with @Contract decorator")
    print("  • Integrate into function decorators")


if __name__ == "__main__":
    demo_ffi_validation()

