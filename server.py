import asyncio
import uuid
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn
import os

# Add ffmpeg to PATH for Whisper
try:
    import imageio_ffmpeg
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    ffmpeg_dir = os.path.dirname(ffmpeg_exe)
    if ffmpeg_dir not in os.environ["PATH"]:
        os.environ["PATH"] = ffmpeg_dir + os.pathsep + os.environ["PATH"]
except ImportError:
    pass

from core.state import PatientState
from core.orchestrator import HospitalOrchestrator
from core.transcriber import WhisperTranscriber
from core.voice_generator import VoiceGenerator

app = FastAPI()

# Global orchestrator and tools
orchestrator = HospitalOrchestrator(ollama_model="llama3")
transcriber = WhisperTranscriber(model_size="base")
voice_gen = VoiceGenerator()

# Ensure static directory exists
if not os.path.exists("static"):
    os.makedirs("static")

# Helper to broadcast status
active_connections = []

# Track active pipeline tasks to prevent overlaps
session_locks = {}

async def broadcast_agent_status(agent_name, state):
    data = {
        "type": "agent_update",
        "agent": agent_name,
        "state": state.to_dict()
    }
    
    # If the state has new executed actions that are alerts, generate voice
    if agent_name == "ExecutorAgent" and state.executed_actions:
        vocal_messages = []
        for action in state.executed_actions:
            if action.get("type") in ["alert_staff", "notify_patient"]:
                msg = action.get("message")
                if msg and msg not in vocal_messages:
                    vocal_messages.append(msg)
        
        if vocal_messages:
            full_message = " ".join(vocal_messages)
            try:
                voice_b64 = voice_gen.text_to_speech_base64(full_message)
                data["audio_alert"] = voice_b64
            except Exception as e:
                print(f"Voice gen error: {e}")

    # Broadicast to all, but handle dead connections
    to_remove = []
    for connection in active_connections:
        try:
            await connection.send_text(json.dumps(data, default=str))
        except Exception:
            to_remove.append(connection)
            
    for conn in to_remove:
        if conn in active_connections:
            active_connections.remove(conn)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    
    session_id = str(uuid.uuid4())[:8]
    await websocket.send_text(json.dumps({
        "type": "session_started",
        "session_id": session_id
    }))

    async def handle_pipeline(state, is_final):
        # Prevent overlapping pipeline runs for the same session
        if session_id in session_locks and not is_final:
            print(f"Skipping live update for {session_id} as a pipeline is already running.")
            return

        session_locks[session_id] = True
        try:
            await orchestrator.run_pipeline(
                state,
                on_agent_complete=broadcast_agent_status,
                max_agents=None if is_final else 2
            )
        finally:
            if session_id in session_locks:
                del session_locks[session_id]

    try:
        while True:
            message_data = await websocket.receive()
            
            if "text" in message_data:
                msg = json.loads(message_data["text"])
                
                if msg.get("type") == "manual_transcript":
                    text = msg.get("text")
                    state = PatientState(session_id=session_id, transcript=text)
                    asyncio.create_task(handle_pipeline(state, True))
                
                elif msg.get("type") == "audio_transcript":
                    import base64
                    audio_bytes = base64.b64decode(msg.get("audio"))
                    is_final = msg.get("is_final", True)
                    
                    # Transcribe
                    text = transcriber.transcribe(audio_bytes)
                    
                    if text:
                        await websocket.send_text(json.dumps({
                            "type": "transcription_result",
                            "text": text,
                            "is_final": is_final
                        }))
                        
                        state = PatientState(session_id=session_id, transcript=text)
                        # We use create_task to avoid blocking the receiver loop
                        asyncio.create_task(handle_pipeline(state, is_final))
            
            elif "bytes" in message_data:
                audio_bytes = message_data["bytes"]
                text = transcriber.transcribe(audio_bytes)
                if text:
                    await websocket.send_text(json.dumps({
                        "type": "transcription_result",
                        "text": text,
                        "is_final": True
                    }))
                    state = PatientState(session_id=session_id, transcript=text)
                    asyncio.create_task(handle_pipeline(state, True))
                    
    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"WS Error for {session_id}: {e}")
    finally:
        if websocket in active_connections:
            active_connections.remove(websocket)
        if session_id in session_locks:
            del session_locks[session_id]

@app.get("/")
async def get():
    with open("static/index.html", "r") as f:
        return HTMLResponse(content=f.read())

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
