import sqlite3

def init_database():
    """Execute schema.sql against beatlink.db to set up tables and indexes."""
    print("Initializing beatlink.db from schema.sql...")
    with open("schema.sql", "r", encoding="utf-8") as f:
        schema = f.read()

    conn = sqlite3.connect("beatlink.db")
    cursor = conn.cursor()
    cursor.executescript(schema)
    conn.commit()
    conn.close()
    print("Database beatlink.db initialized successfully!")

if __name__ == "__main__":
    init_database()
