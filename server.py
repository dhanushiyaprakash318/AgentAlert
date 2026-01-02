import asyncio
import uuid
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn
import os

from core.state import PatientState
from core.orchestrator import HospitalOrchestrator

app = FastAPI()

# Global orchestrator
orchestrator = HospitalOrchestrator(ollama_model="llama3")

# Ensure static directory exists
if not os.path.exists("static"):
    os.makedirs("static")

# Helper to broadcast status
active_connections = []

async def broadcast_agent_status(agent_name, state):
    data = {
        "type": "agent_update",
        "agent": agent_name,
        "state": state.to_dict()
    }
    for connection in active_connections:
        await connection.send_text(json.dumps(data, default=str))

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    
    session_id = str(uuid.uuid4())[:8]
    await websocket.send_text(json.dumps({
        "type": "session_started",
        "session_id": session_id
    }))

    try:
        while True:
            # Receive manual text inputs
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "manual_transcript":
                # Run a one-off pipeline for the manual text
                text = message.get("text")
                state = PatientState(session_id=session_id, transcript=text)
                await orchestrator.run_pipeline(
                    state,
                    on_agent_complete=broadcast_agent_status
                )
                
    except WebSocketDisconnect:
        active_connections.remove(websocket)
    except Exception as e:
        print(f"WS Error: {e}")
        if websocket in active_connections:
            active_connections.remove(websocket)

@app.get("/")
async def get():
    with open("static/index.html", "r") as f:
        return HTMLResponse(content=f.read())

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
