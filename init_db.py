import os
from dotenv import load_dotenv
from cs50 import SQL

load_dotenv()

def init_database():
    """Execute schema.sql against PostgreSQL database to set up tables and indexes."""
    print("Initializing PostgreSQL database from schema.sql...")
    with open("schema.sql", "r", encoding="utf-8") as f:
        schema = f.read()

    db_url = os.environ.get(
        "DATABASE_URL",
        "postgresql://neondb_owner:npg_loSOMK7De4kN@ep-red-cell-berd34rb.c-9.us-east-2.aws.neon.tech/neondb?sslmode=require"
    )
    if db_url.startswith("postgresql://") and not db_url.startswith("postgresql+"):
        db_url = db_url.replace("postgresql://", "postgresql+psycopg2://", 1)

    db = SQL(db_url)

    # Execute individual SQL statements separated by semicolon
    statements = [stmt.strip() for stmt in schema.split(";") if stmt.strip()]
    for stmt in statements:
        db.execute(stmt)

    print("PostgreSQL database initialized successfully!")

if __name__ == "__main__":
    init_database()
