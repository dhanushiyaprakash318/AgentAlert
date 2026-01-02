import re
from core.base import BaseAgent
from core.state import PatientState

class DetectorAgent(BaseAgent):
    """
    Identifies symptoms and patient intent from the transcript.
    """
    def __init__(self):
        super().__init__("DetectorAgent")
        # Synthetic symptom keywords for risk detection
        self.symptom_keywords = {
            "chest pain": "cardiac",
            "shortness of breath": "respiratory",
            "difficulty breathing": "respiratory",
            "dizziness": "neurological",
            "severe headache": "neurological",
            "bleeding": "trauma",
            "fever": "infection",
            "cough": "respiratory",
            "nausea": "gastrointestinal"
        }

    async def process(self, state: PatientState) -> PatientState:
        if not state.transcript:
            self.log(state, "No transcript available for detection.")
            return state

        text = state.transcript.lower()
        
        # 1. Detect Symptoms
        detected_symptoms = []
        for symptom in self.symptom_keywords:
            if re.search(rf"\b{symptom}\b", text):
                detected_symptoms.append(symptom)
        
        state.symptoms = list(set(detected_symptoms))
        
        # 2. Detect Intent (Simple heuristic)
        if any(word in text for word in ["help", "emergency", "pain", "hurts"]):
            state.intent = "Requesting Assistance"
        elif any(word in text for word in ["check", "status", "when"]):
            state.intent = "Status Inquiry"
        else:
            state.intent = "General Communication"

        self.log(state, f"Detected Symptoms: {state.symptoms}, Intent: {state.intent}")
        return state
