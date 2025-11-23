import sqlite3
from contextlib import contextmanager

DATABASE_FILE = "hackathon_data.db"

# --- Database Connection Management ---

@contextmanager
def get_db_connection():
    """
    Provides a managed SQLite database connection using a context manager.
    The connection is automatically committed and closed when exiting the 'with' block.
    """
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        conn.row_factory = sqlite3.Row 
        conn.execute("PRAGMA journal_mode=WAL")
        yield conn
        conn.commit()
    except sqlite3.Error as e:
        print(f"Database error occurred: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()

# --- Database Initialization ---

def initialize_db():
    """
    Initializes the database by creating the necessary table if it doesn't exist.
    We are creating a simple table to store logs/data posted by different services.
    """
    print(f"Initializing database at: {DATABASE_FILE}...")
    try:
        with get_db_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS data_entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    prompt_id INTEGER NOT NULL,
                    prompt TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    rejected_answer TEXT NOT NULL,
                    refusal INTEGER NOT NULL,
                    guard_rating INTEGER NOT NULL,
                    guard_model TEXT NOT NULL,
                    model TEXT NOT NULL,
                    timestamp TEXT
                )
            """)
        print("Database schema created successfully (Table: data_entries).")
    except Exception as e:
        print(f"Failed to initialize database: {e}")