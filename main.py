import asyncio
import uuid
import sys
from core.state import PatientState
from core.orchestrator import HospitalOrchestrator

async def main():
    print("====================================================")
    print("  AGENTIC PATIENT RISK DETECTION & ALERTING SYSTEM  ")
    print("====================================================")
    print("Real-time voice-activated monitoring started.")
    print("TIP: Run 'python server.py' for the visual dashboard.")
    print("Press Ctrl+C to stop.")
    
    # Initialize the orchestrator
    orchestrator = HospitalOrchestrator(ollama_model="llama3")
    
    try:
        while True:
            # Create a new state for each "breath" or "incident" 
            # In a real system, this would be a continuous stream window
            session_id = str(uuid.uuid4())[:8]
            state = PatientState(session_id=session_id)
            
            # Run the agent pipeline
            # 1. Listen (waits for voice activity)
            # 2. Reason
            # 3. Plan
            # 4. Act
            # 5. Respond
            await orchestrator.run_pipeline(state)
            
            print(f"\n[SYSTEM] Ready for next input...\n")
            
    except KeyboardInterrupt:
        print("\nShutting down safely...")
    except Exception as e:
        print(f"\nCritical Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
