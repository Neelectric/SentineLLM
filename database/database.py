import sqlite3
from contextlib import contextmanager

# Configuration for the SQLite database file
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
        # Connect to the SQLite database file. It will be created if it doesn't exist.
        conn = sqlite3.connect(DATABASE_FILE)
        # Set row_factory to sqlite3.Row to allow accessing columns by name
        conn.row_factory = sqlite3.Row 
        conn.execute("PRAGMA journal_mode=WAL") # WAL improves write concurrency, useful for multiple services
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
                    service_name TEXT NOT NULL,
                    data_payload TEXT NOT NULL,
                    timestamp TEXT NOT NULL
                )
            """)
        print("Database schema created successfully (Table: data_entries).")
    except Exception as e:
        print(f"Failed to initialize database: {e}")

# If this file is run directly, initialize the database
if __name__ == "__main__":
    initialize_db()

# Example usage of the context manager (you'll use this pattern in FastAPI)
# if __name__ == "__main__":
#     initialize_db()
#     try:
#         with get_db_connection() as conn:
#             # Insert a test record
#             cursor = conn.cursor()
#             cursor.execute(
#                 "INSERT INTO data_entries (service_name, data_payload, timestamp) VALUES (?, ?, ?)",
#                 ("TestService", '{"temp": 25.5, "status": "OK"}', '2025-01-01T12:00:00Z')
#             )
#             print("Test record inserted.")
#     except Exception as e:
#         print(f"Error during test insertion: {e}")