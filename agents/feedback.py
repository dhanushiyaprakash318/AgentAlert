import pyttsx3
from core.base import BaseAgent
from core.state import PatientState

class FeedbackAgent(BaseAgent):
    """
    Feedback & Observation Agent.
    Responds to the patient using synthesized voice.
    """
    def __init__(self, rate=150):
        super().__init__("FeedbackAgent")
        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', rate)
        except Exception as e:
            print(f"Failed to initialize TTS engine: {e}")
            self.engine = None

    async def process(self, state: PatientState) -> PatientState:
        if not state.response_text:
            # Default response if nothing planned
            if state.risk_level in ["High", "Critical"]:
                state.response_text = "I have alerted the clinical staff. Help is on the way. Please stay calm."
            else:
                state.response_text = "Thank you for sharing. I have logged your information for the clinical team."

        self.log(state, f"Responding: \"{state.response_text}\"")
        
        if self.engine:
            try:
                self.engine.say(state.response_text)
                self.engine.runAndWait()
            except Exception as e:
                self.log(state, f"TTS Error: {str(e)}")
        else:
            self.log(state, "TTS skipped - Engine not initialized.")

        state.observations.append(f"Responded to patient: {state.response_text}")
        return state
