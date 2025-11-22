from fastapi import FastAPI, HTTPException, Body
from datetime import datetime
from typing import List, Dict, Any
from database import initialize_db, get_db_connection
from metric_exporter import start_metrics_server, register_data_finding, reset_findings

from olmo_trace import olmo_trace

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
        "prompt_id": "1", 
        "prompt": "1,2",
        "answer": "3",
        "refusal": False,
        "guard_rating": "safe",
        "guard_model": "qwen",
        "model": "OLMO"
    }
)):
    """
    Receives raw JSON data and logs it to the 'data_entries' table.
    Expects 'service_name' (str) and 'data_payload' (dict) in the request body.
    """
    #print("a")
    pre_train_docs = olmo_trace(model, prompt, answer)
    
    try:
        prompt_id = entry["prompt_id"]
        prompt = entry["prompt"]
        answer = entry["answer"]
        refusal = entry["refusal"]
        guard_rating = 1 if entry["guard_rating"] == "safe" else 0
        guard_model = entry["guard_model"]
        model = entry["model"]
    except KeyError as e:
        raise HTTPException(status_code=422, detail=f"Missing required field: {e.args[0]}")
    except TypeError:
        raise HTTPException(status_code=400, detail="Request body must be a JSON object with 'service_name' and 'data_payload'.")

    current_time = datetime.now().isoformat()

    try:
        # Use the context manager to get a connection and safely commit/close
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO data_entries (prompt_id, prompt, answer, refusal, guard_rating, guard_model, model, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (prompt_id, prompt, answer, refusal, guard_rating, guard_model, model, current_time)
            )
            # The context manager will handle conn.commit()
            new_id = cursor.lastrowid
            register_data_finding(model, guard_model)
            
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
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM data_entries ORDER BY timestamp DESC")
            rows = cursor.fetchall()
            data_entries = [dict(row) for row in rows]
            
            return data_entries

    except Exception as e:
        print(f"Error fetching data: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve data due to an internal database error.")
    
@app.get("/data_unsafe", response_model=List[Dict[str, Any]])
def get_all_data() -> List[Dict[str, Any]]:
    """
    Retrieves all unsafe data entries from the 'data_entries' table as a list of dictionaries.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM data_entries WHERE guard_rating = 0 ORDER BY timestamp DESC")
            rows = cursor.fetchall()
            data_entries = [dict(row) for row in rows]
            
            return data_entries

    except Exception as e:
        print(f"Error fetching data: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve data due to an internal database error.")
    
@app.options("/wipedb", response_model=bool)
def wipe_db() -> bool:
    print("database wipe")
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM data_entries")
            cursor.execute("UPDATE sqlite_sequence SET seq = 0 WHERE name = 'data_entries'")
            reset_findings()

            return True
        
    except Exception as e:
        print(f"Error deleting data: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete data due to an internal database error.")
    
@app.options("/refine")
def refine_data():
    print("Now the cool stuff should happen")    

# --- 4. Server Execution ---
if __name__ == "__main__":
    import uvicorn
    start_metrics_server()
    uvicorn.run("main:app", host="0.0.0.0", port=8003)
    