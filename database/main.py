from fastapi import FastAPI, HTTPException, Body
import json
from datetime import datetime
from typing import List, Dict, Any
from db_setup import initialize_db, get_db_connection

# --- 1. FastAPI Initialization ---

# Initialize the FastAPI application
app = FastAPI(
    title="JailBreaking Prompt Database",
    description="",
    version="1.0.0"
)

# --- 2. FastAPI Event Handlers ---

@app.on_event("startup")
def startup_event():
    """
    Ensures the SQLite database and necessary tables are created.
    """
    initialize_db()
    print("FastAPI application started. Database initialized.")

# --- 3. API Endpoints ---

@app.post("/data", status_code=201)
def post_data_entry(entry: Dict[str, Any] = Body(
    ..., 
    example={
        "service_name": "SensorMonitor_01", 
        "data_payload": {"temperature": 28.5, "humidity": 65, "status": "Running"}
    }
)):
    """
    Receives raw JSON data and logs it to the 'data_entries' table.
    Expects 'service_name' (str) and 'data_payload' (dict) in the request body.
    """
    try:
        service_name = entry["service_name"]
        data_payload = entry["data_payload"]
    except KeyError as e:
        raise HTTPException(status_code=422, detail=f"Missing required field: {e.args[0]}")
    except TypeError:
        raise HTTPException(status_code=400, detail="Request body must be a JSON object with 'service_name' and 'data_payload'.")

    try:
        payload_json = json.dumps(data_payload)
    except TypeError:
        raise HTTPException(status_code=400, detail="data_payload must be a serializable dictionary.")

    current_time = datetime.now().isoformat()

    try:
        # Use the context manager to get a connection and safely commit/close
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO data_entries (service_name, data_payload, timestamp)
                VALUES (?, ?, ?)
                """,
                (service_name, payload_json, current_time)
            )
            # The context manager will handle conn.commit()
            new_id = cursor.lastrowid
            
        return {
            "message": "Data logged successfully",
            "id": new_id,
            "timestamp": current_time
        }

    except Exception as e:
        print(f"Error inserting data: {e}")
        raise HTTPException(status_code=500, detail="Failed to log data due to an internal database error.")


@app.get("/data", response_model=List[Dict[str, Any]])
def get_all_data() -> List[Dict[str, Any]]:
    """
    Retrieves all data entries from the 'data_entries' table as a list of dictionaries.
    The 'data_payload' field will still be a JSON string as stored in the DB.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, service_name, data_payload, timestamp FROM data_entries ORDER BY timestamp DESC")
            rows = cursor.fetchall()
            data_entries = [dict(row) for row in rows]
            
            return data_entries

    except Exception as e:
        print(f"Error fetching data: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve data due to an internal database error.")