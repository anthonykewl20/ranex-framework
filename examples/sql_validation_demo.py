#!/usr/bin/env python3
"""
Ranex Framework - SQL Validation Demo

This demo showcases SQL query validation capabilities.
It demonstrates:
1. Query validation before execution
2. Table existence checking
3. Column existence checking
4. SQL syntax validation
5. Database hallucination prevention

Run: python examples/sql_validation_demo.py
"""

import os
import tempfile
import sqlite3
from ranex_core import DatabaseSchemaProvider


def create_test_database():
    """Create a test SQLite database for demo purposes."""
    fd, db_path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create test tables
    cursor.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            email TEXT NOT NULL,
            name TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE products (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            price REAL
        )
    """)
    
    conn.commit()
    conn.close()
    
    return db_path


def demo_sql_validation():
    """Demonstrate SQL validation capabilities."""
    print("=" * 70)
    print("Ranex Framework - SQL Validation Demo")
    print("=" * 70)
    print()
    
    db_path = create_test_database()
    print(f"Created test database: {db_path}")
    
    provider = DatabaseSchemaProvider(f"sqlite://{db_path}")
    print("✅ Database schema provider initialized")
    print()
    
    # Demo 1: Valid queries
    print("📝 Demo 1: Valid SQL Queries")
    print("-" * 70)
    
    valid_queries = [
        "SELECT * FROM users",
        "SELECT id, email FROM users WHERE id = 1",
        "SELECT * FROM products WHERE price > 100",
        "SELECT u.name, p.name FROM users u JOIN products p ON u.id = p.id",
    ]
    
    print("Testing valid queries:")
    for query in valid_queries:
        try:
            result = provider.validate_query(query)
            print(f"  ✅ Valid: {query[:50]}...")
            print(f"     {result}")
        except Exception as e:
            print(f"  ❌ Unexpected error: {query[:50]}...")
            print(f"     {e}")
    print()
    
    # Demo 2: Invalid table names (hallucination detection)
    print("📝 Demo 2: Database Hallucination Detection")
    print("-" * 70)
    
    invalid_queries = [
        "SELECT * FROM customers",  # Table doesn't exist
        "SELECT * FROM orders",     # Table doesn't exist
        "SELECT * FROM non_existent_table",
    ]
    
    print("Testing queries with non-existent tables:")
    for query in invalid_queries:
        try:
            result = provider.validate_query(query)
            print(f"  ⚠️  Unexpected: {query} was accepted")
        except Exception as e:
            print(f"  ✅ Blocked: {query}")
            print(f"     Error: {str(e)[:80]}...")
    print()
    
    # Demo 3: SQL syntax validation
    print("📝 Demo 3: SQL Syntax Validation")
    print("-" * 70)
    
    syntax_errors = [
        "SELECT * FROM",  # Missing table name
        "SELECT FROM users",  # Missing columns
        "SELECT * users",  # Missing FROM keyword
    ]
    
    print("Testing queries with syntax errors:")
    for query in syntax_errors:
        try:
            result = provider.validate_query(query)
            print(f"  ⚠️  Unexpected: {query} was accepted")
        except Exception as e:
            print(f"  ✅ Blocked: {query}")
            print(f"     Error: {str(e)[:80]}...")
    print()
    
    # Demo 4: Benefits of validation
    print("📝 Demo 4: Benefits of SQL Validation")
    print("-" * 70)
    print("SQL validation prevents:")
    print("  • Database hallucinations (non-existent tables)")
    print("  • Runtime errors from invalid queries")
    print("  • Security vulnerabilities (SQL injection)")
    print("  • Performance issues (missing indexes)")
    print()
    print("Use cases:")
    print("  • AI code generation (validate before execution)")
    print("  • Query builder validation")
    print("  • Migration script validation")
    print("  • API endpoint validation")
    print()
    
    # Demo 5: Integration example
    print("📝 Demo 5: Integration Example")
    print("-" * 70)
    print("""
# Example: Validate SQL before execution

from ranex_core import DatabaseSchemaProvider

provider = DatabaseSchemaProvider("sqlite:///app.db")

def execute_safe_query(query: str):
    # Validate before execution
    try:
        result = provider.validate_query(query)
        print(f"✅ Query validated: {result}")
        
        # Now execute safely
        # cursor.execute(query)
        return True
    except Exception as e:
        print(f"❌ Query validation failed: {e}")
        return False

# Usage
execute_safe_query("SELECT * FROM users")  # ✅ Valid
execute_safe_query("SELECT * FROM customers")  # ❌ Invalid (table doesn't exist)
""")
    print()
    
    # Demo 6: Multi-database validation
    print("📝 Demo 6: Multi-Database Validation")
    print("-" * 70)
    print("Validation works with:")
    print("  • PostgreSQL (uses PostgreSQL dialect)")
    print("  • MySQL (uses MySQL dialect)")
    print("  • SQLite (uses SQLite dialect)")
    print("  • Redis (skips validation - NoSQL)")
    print()
    print("Each database type uses appropriate:")
    print("  • SQL dialect")
    print("  • Schema inspection method")
    print("  • Validation rules")
    print()
    
    # Cleanup
    os.unlink(db_path)
    
    print("=" * 70)
    print("✅ Demo Complete!")
    print("=" * 70)
    print()
    print("Key Takeaways:")
    print("  • SQL validation prevents runtime errors")
    print("  • Detects database hallucinations")
    print("  • Validates syntax and schema")
    print("  • Supports multiple database types")
    print()
    print("Next Steps:")
    print("  • Try examples/database_schema_demo.py for schema inspection")
    print("  • Integrate into query builders")
    print("  • Use for AI code generation validation")


if __name__ == "__main__":
    demo_sql_validation()

