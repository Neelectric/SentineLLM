from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import json

# Initialize the FastAPI application
app = FastAPI(title="Grafana Test Backend")

# --- CORS Configuration ---
# You MUST add this to allow Grafana (running on port 3000) to communicate 
# with this backend (running on port 8000).
origins = [
    "http://localhost:3000",  # Your Grafana host and port
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       # Specifies which origins can make requests
    allow_credentials=True,      # Allows cookies/auth headers
    allow_methods=["*"],         # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],         # Allows all headers
)

# --- POST Endpoint ---
@app.post("/button-action")
async def handle_button_press(request: Request):
    """
    Handles POST requests from Grafana.
    """
    # 1. Log the endpoint access
    print("\n-------------------------------------------------")
    print("✅ POST request received on /button-action endpoint")
    
    # 2. Log the incoming request body (payload)
    try:
        # Get the JSON body from the request
        request_body = await request.json()
        print(f"Payload received:")
        # Pretty print the JSON payload
        print(json.dumps(request_body, indent=4))
    except json.JSONDecodeError:
        print("No valid JSON payload received.")
    
    # 3. Log the request headers (helpful for debugging)
    print(f"Client IP: {request.client.host}")
    print("-------------------------------------------------")

    return {"status": "success", "message": "Command executed and logged."}

if __name__ == "__main__":
    import uvicorn
    # The default host and port for FastAPI is typically 127.0.0.1:8000
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)