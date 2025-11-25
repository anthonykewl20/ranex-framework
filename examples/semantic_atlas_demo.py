#!/usr/bin/env python3
"""
Ranex Framework - Semantic Atlas Demo

This demo showcases semantic code search and codebase indexing.
It demonstrates:
1. Codebase indexing
2. Semantic search
3. Function deduplication
4. Code mapping

Run: python examples/semantic_atlas_demo.py
"""

import os
from ranex_core import SemanticAtlas


def demo_semantic_atlas():
    """Demonstrate semantic atlas capabilities."""
    print("=" * 70)
    print("Ranex Framework - Semantic Atlas Demo")
    print("=" * 70)
    print()
    
    # Initialize atlas
    try:
        atlas = SemanticAtlas.load()
        print("✅ Semantic atlas initialized")
    except Exception as e:
        print(f"⚠️  Atlas initialization: {e}")
        atlas = SemanticAtlas()
        print("✅ Semantic atlas created (new instance)")
    print()
    
    # Demo 1: Semantic search
    print("📝 Demo 1: Semantic Search")
    print("-" * 70)
    
    search_queries = [
        "validate email address",
        "process payment",
        "authenticate user",
        "send notification",
    ]
    
    print("Semantic search examples:")
    for query in search_queries:
        try:
            results = atlas.semantic_search(query, threshold=0.7)
            print(f"  Query: '{query}'")
            print(f"    Results: {len(results)} functions found")
            if results:
                for result in results[:3]:
                    print(f"      • {result}")
            else:
                print("      (No results - atlas may need indexing)")
        except Exception as e:
            print(f"  ⚠️  Search error: {e}")
        print()
    
    # Demo 2: Commons functions
    print("📝 Demo 2: Commons Functions")
    print("-" * 70)
    
    try:
        commons = SemanticAtlas.get_commons_functions()
        print(f"Found {len(commons)} commons functions:")
        for func in commons[:10]:
            print(f"  • {func}")
        if len(commons) > 10:
            print(f"  ... and {len(commons) - 10} more")
    except Exception as e:
        print(f"⚠️  Error getting commons functions: {e}")
    print()
    
    # Demo 3: Code deduplication
    print("📝 Demo 3: Code Deduplication")
    print("-" * 70)
    print("Semantic atlas helps prevent code duplication:")
    print()
    print("  Before using atlas:")
    print("    • Developer writes: validate_email()")
    print("    • Another developer writes: check_email_format()")
    print("    • Result: Duplicate code")
    print()
    print("  After using atlas:")
    print("    • Search: 'validate email'")
    print("    • Find: validate_email() already exists")
    print("    • Result: Reuse existing function")
    print()
    
    # Demo 4: Codebase mapping
    print("📝 Demo 4: Codebase Mapping")
    print("-" * 70)
    print("Semantic atlas provides:")
    print("  • Function location mapping")
    print("  • Dependency tracking")
    print("  • Feature discovery")
    print("  • Code reuse opportunities")
    print()
    print("Use cases:")
    print("  • Find existing implementations")
    print("  • Understand codebase structure")
    print("  • Prevent duplication")
    print("  • Refactoring assistance")
    print()
    
    # Demo 5: Integration example
    print("📝 Demo 5: Integration Example")
    print("-" * 70)
    print("""
# Example: Check for existing function before creating new one

from ranex_core import SemanticAtlas

atlas = SemanticAtlas.load()

def create_function_if_needed(intent: str):
    # Search for existing implementations
    results = atlas.semantic_search(intent, threshold=0.8)
    
    if results:
        print(f"✅ Found existing function: {results[0]}")
        print("   Reuse instead of creating new one")
        return results[0]
    else:
        print("✅ No existing function found")
        print("   Safe to create new function")
        return None

# Usage
create_function_if_needed("validate email address")
create_function_if_needed("process payment transaction")
""")
    print()
    
    print("=" * 70)
    print("✅ Demo Complete!")
    print("=" * 70)
    print()
    print("Key Takeaways:")
    print("  • Semantic atlas enables code discovery")
    print("  • Prevents code duplication")
    print("  • Maps codebase structure")
    print("  • Supports refactoring")
    print()
    print("Next Steps:")
    print("  • Try examples/circular_imports_demo.py for cycle detection")
    print("  • Use for code discovery before writing new functions")
    print("  • Integrate into development workflow")


if __name__ == "__main__":
    demo_semantic_atlas()

