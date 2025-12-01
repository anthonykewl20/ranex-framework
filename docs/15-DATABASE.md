# Database Support

Ranex Community Edition includes database schema discovery and SQL validation.

---

## Supported Databases

| Database | Schema Discovery | SQL Validation |
|----------|:----------------:|:--------------:|
| SQLite | ✅ | ✅ |
| PostgreSQL | ✅ | ✅ |
| MySQL | ✅ | ✅ |

---

## Schema Discovery

### Auto-Detection

Ranex automatically detects databases in your project:

```bash
# SQLite files are detected automatically
./data/app.db
./db/database.sqlite

# PostgreSQL/MySQL via environment
export RANEX_DB_PRIMARY_URL="postgresql://localhost/mydb"
```

### CLI Check

```bash
ranex doctor
```

Output:
```
Database:
  ✅ SQLite: ./data/app.db
     Tables: users, orders, products, order_items
  ✅ PostgreSQL: localhost/mydb
     Tables: customers, invoices, payments
```

### Python API

```python
from ranex_core import SchemaDiscovery

# SQLite
discovery = SchemaDiscovery()
schema = discovery.discover_sqlite("./data/app.db")

for table in schema.tables:
    print(f"Table: {table.name}")
    for column in table.columns:
        print(f"  - {column.name}: {column.type}")
```

---

## SQL Validation

Validate SQL queries against your database schema.

### Basic Validation

```python
from ranex_core import SqlValidator

validator = SqlValidator()

# Valid query
result = validator.validate("SELECT id, name FROM users WHERE active = true")
print(result.is_valid)  # True

# Invalid query (syntax error)
result = validator.validate("SELEC * FORM users")
print(result.is_valid)  # False
print(result.error)     # "Syntax error at position 0"
```

### Schema-Aware Validation

When connected to a database, Ranex validates column names:

```python
# If 'users' table has columns: id, name, email, created_at

# Valid - all columns exist
validator.validate("SELECT id, name FROM users")  # ✅

# Invalid - 'username' doesn't exist
validator.validate("SELECT id, username FROM users")  
# Error: Column 'username' not found in table 'users'
```

---

## Database Configuration

### Environment Variables

```bash
# Primary database
export RANEX_DB_PRIMARY_URL="postgresql://user:pass@localhost:5432/mydb"

# Read replica (optional)
export RANEX_DB_REPLICA_URL="postgresql://user:pass@replica.host:5432/mydb"

# SQLite (auto-detected, but can specify)
export RANEX_DB_SQLITE_PATH="./data/app.db"
```

### Configuration File

```toml
# .ranex/config.toml
[databases]
primary = "postgresql://localhost/main"
replica = "postgresql://localhost/replica"
sqlite_path = "./data/local.db"
```

### Database Aliases

Name your databases for easy reference:

```toml
# .ranex/config.toml
[database.aliases]
main = "postgresql://localhost/main"
analytics = "postgresql://localhost/analytics"
cache = "redis://localhost:6379"
```

Access via MCP:
```
MCP Tool: list_db_aliases
Result: main, analytics, cache
```

---

## Connection String Format

### PostgreSQL

```
postgresql://username:password@host:port/database

# Examples
postgresql://localhost/mydb
postgresql://admin:secret@db.example.com:5432/production
postgresql://user:pass@localhost/dev?sslmode=require
```

### MySQL

```
mysql://username:password@host:port/database

# Examples
mysql://localhost/mydb
mysql://root:password@127.0.0.1:3306/app
```

### SQLite

```
# Direct path
./data/app.db
/absolute/path/to/database.sqlite

# URI format
sqlite:///./data/app.db
sqlite:////absolute/path/database.db
```

---

## Using with MCP

### list_db_aliases

Lists configured database aliases.

```json
{
  "tool": "list_db_aliases"
}
```

Response:
```json
{
  "aliases": ["main", "analytics", "cache"],
  "primary": "main"
}
```

### validate_sql

Validates a SQL query.

```json
{
  "tool": "validate_sql",
  "query": "SELECT id, name FROM users WHERE status = 'active'"
}
```

Response:
```json
{
  "valid": true,
  "query_type": "SELECT",
  "tables": ["users"],
  "columns": ["id", "name"]
}
```

---

## Common Patterns

### Pattern 1: SQLite for Development

```python
# config.py
import os

if os.environ.get("ENV") == "production":
    DATABASE_URL = os.environ["DATABASE_URL"]  # PostgreSQL
else:
    DATABASE_URL = "sqlite:///./data/dev.db"  # Local SQLite
```

### Pattern 2: Multiple Databases

```python
# app/database.py
from sqlalchemy import create_engine

# Main database for transactions
main_engine = create_engine(os.environ["RANEX_DB_PRIMARY_URL"])

# Read replica for queries
replica_engine = create_engine(os.environ.get("RANEX_DB_REPLICA_URL", 
                                               os.environ["RANEX_DB_PRIMARY_URL"]))
```

### Pattern 3: Validate Before Execute

```python
from ranex_core import SqlValidator

validator = SqlValidator()

def safe_execute(query: str, params: dict):
    # Validate first
    result = validator.validate(query)
    if not result.is_valid:
        raise ValueError(f"Invalid SQL: {result.error}")
    
    # Execute if valid
    return db.execute(query, params)
```

---

## Security Considerations

### 1. Never Hardcode Credentials

```python
# ❌ BAD
DATABASE_URL = "postgresql://admin:password123@localhost/mydb"

# ✅ GOOD
DATABASE_URL = os.environ["DATABASE_URL"]
```

### 2. Use Parameterized Queries

```python
# ❌ BAD - SQL Injection vulnerable
query = f"SELECT * FROM users WHERE id = {user_id}"

# ✅ GOOD - Parameterized
query = "SELECT * FROM users WHERE id = %s"
cursor.execute(query, (user_id,))
```

### 3. Limit Database Permissions

```sql
-- Create read-only user for validation
CREATE USER ranex_readonly WITH PASSWORD 'readonly';
GRANT SELECT ON ALL TABLES IN SCHEMA public TO ranex_readonly;
```

---

## Troubleshooting

### "Cannot connect to database"

Check your connection string:
```bash
# Test with psql
psql "postgresql://user:pass@localhost/mydb"

# Check environment variable
echo $RANEX_DB_PRIMARY_URL
```

### "Table not found"

Ensure schema is up to date:
```bash
ranex doctor
```

### "Permission denied"

Verify database user has SELECT permissions:
```sql
GRANT SELECT ON ALL TABLES IN SCHEMA public TO your_user;
```

---

## API Reference

### SqlValidator

```python
from ranex_core import SqlValidator

validator = SqlValidator()

# Validate query
result = validator.validate("SELECT * FROM users")
print(result.is_valid)  # bool
print(result.error)     # str or None
print(result.query_type)  # "SELECT", "INSERT", etc.
```

### SchemaDiscovery

```python
from ranex_core import SchemaDiscovery

discovery = SchemaDiscovery()

# Discover SQLite schema
schema = discovery.discover_sqlite("./data/app.db")

# Access tables
for table in schema.tables:
    print(table.name)
    for col in table.columns:
        print(f"  {col.name}: {col.type}")
```

---

## Next Steps

- [Security Scanning](./12-SECURITY-SCANNING.md) - SQL injection detection
- [CLI Reference](./20-CLI-REFERENCE.md) - Database commands
- [FastAPI Integration](./33-FASTAPI-INTEGRATION.md) - Full stack setup

