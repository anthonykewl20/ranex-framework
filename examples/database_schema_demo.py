#!/usr/bin/env python3
"""
Ranex Framework - Database Schema Demo

This demo showcases database schema inspection capabilities.
It demonstrates:
1. Multi-database support (PostgreSQL, MySQL, SQLite, Redis)
2. Schema inspection
3. Table discovery
4. Column discovery

Run: python examples/database_schema_demo.py
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
            name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE products (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            price REAL,
            stock INTEGER DEFAULT 0
        )
    """)
    
    cursor.execute("""
        CREATE TABLE orders (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            product_id INTEGER,
            quantity INTEGER,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    """)
    
    conn.commit()
    conn.close()
    
    return db_path


def demo_database_schema():
    """Demonstrate database schema inspection."""
    print("=" * 70)
    print("Ranex Framework - Database Schema Demo")
    print("=" * 70)
    print()
    
    # Demo 1: SQLite schema inspection
    print("📝 Demo 1: SQLite Schema Inspection")
    print("-" * 70)
    
    db_path = create_test_database()
    print(f"Created test database: {db_path}")
    
    try:
        provider = DatabaseSchemaProvider(f"sqlite://{db_path}")
        schema = provider.get_schema_context()
        
        print(f"✅ Schema inspection completed")
        print(f"   Tables found: {len(schema.tables)}")
        print()
        
        print("Database Schema:")
        for table_name, columns in schema.tables.items():
            print(f"  Table: {table_name}")
            for col in columns:
                print(f"    - {col.name}: {col.dtype}")
            print()
    except Exception as e:
        print(f"⚠️  Schema inspection error: {e}")
    finally:
        os.unlink(db_path)
    print()
    
    # Demo 2: Multi-database support
    print("📝 Demo 2: Multi-Database Support")
    print("-" * 70)
    print("Ranex supports multiple database types:")
    print()
    print("✅ Supported Databases:")
    print("  • PostgreSQL: postgresql://user:pass@host:5432/dbname")
    print("  • MySQL: mysql://user:pass@host:3306/dbname")
    print("  • SQLite: sqlite:///path/to/database.db")
    print("  • Redis: redis://host:6379")
    print()
    print("Example usage:")
    print("""
# PostgreSQL
provider = DatabaseSchemaProvider("postgresql://user:pass@localhost:5432/mydb")
schema = provider.get_schema_context()

# MySQL
provider = DatabaseSchemaProvider("mysql://user:pass@localhost:3306/mydb")
schema = provider.get_schema_context()

# SQLite
provider = DatabaseSchemaProvider("sqlite:///path/to/database.db")
schema = provider.get_schema_context()

# Redis
provider = DatabaseSchemaProvider("redis://localhost:6379")
schema = provider.get_schema_context()
""")
    print()
    
    # Demo 3: Schema context usage
    print("📝 Demo 3: Schema Context Usage")
    print("-" * 70)
    print("Schema context provides:")
    print("  • Table names")
    print("  • Column names and types")
    print("  • Foreign key relationships")
    print("  • Index information")
    print()
    print("Use cases:")
    print("  • Validate SQL queries before execution")
    print("  • Generate type-safe database clients")
    print("  • Detect schema drift")
    print("  • Auto-complete table/column names")
    print()
    
    # Demo 4: Integration example
    print("📝 Demo 4: Integration Example")
    print("-" * 70)
    print("""
# Example: Validate SQL before execution

from ranex_core import DatabaseSchemaProvider

provider = DatabaseSchemaProvider("sqlite:///app.db")
schema = provider.get_schema_context()

# Check if table exists
if "users" not in schema.tables:
    print("❌ Table 'users' does not exist")
    sys.exit(1)

# Check if column exists
user_columns = [col.name for col in schema.tables["users"]]
if "email" not in user_columns:
    print("❌ Column 'email' does not exist in 'users' table")
    sys.exit(1)

print("✅ Schema validation passed")
""")
    print()
    
    print("=" * 70)
    print("✅ Demo Complete!")
    print("=" * 70)
    print()
    print("Key Takeaways:")
    print("  • Multi-database support (PostgreSQL, MySQL, SQLite, Redis)")
    print("  • Automatic schema discovery")
    print("  • Table and column inspection")
    print("  • Type information for columns")
    print()
    print("Next Steps:")
    print("  • Try examples/sql_validation_demo.py for SQL validation")
    print("  • Use schema context for query validation")
    print("  • Integrate into database migration tools")


if __name__ == "__main__":
    demo_database_schema()

