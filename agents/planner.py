from core.base import BaseAgent
from core.state import PatientState

class PlannerAgent(BaseAgent):
    """
    Deterministic rule-based planning for action execution.
    Converts risk level and intent into a set of planned actions.
    """
    def __init__(self):
        super().__init__("PlannerAgent")

    async def process(self, state: PatientState) -> PatientState:
        self.log(state, "Determining action plan based on risk and reasoning...")
        
        actions = []
        
        # Rule 1: High/Critical Risk -> Immediate Nurse/Doctor Alert
        if state.risk_level in ["High", "Critical"]:
            actions.append({
                "type": "alert_staff",
                "priority": "emergency",
                "target": "Nurse Station",
                "message": f"CRITICAL: Patient session {state.session_id} - {state.reasoning}"
            })
            state.human_in_the_loop_required = True
        
        # Rule 2: Symptoms detected but low risk -> Scheduled Check-in
        elif state.risk_level == "Moderate":
            actions.append({
                "type": "alert_staff",
                "priority": "standard",
                "target": "Assigned Nurse",
                "message": f"Observation: Patient session {state.session_id} reports {', '.join(state.symptoms)}."
            })

        # Rule 3: Patient Intent is a Request -> Notification
        if state.intent == "Requesting Assistance":
            actions.append({
                "type": "notify_patient",
                "message": "Assistant: I have received your request and notified the clinical staff. Help is on the way."
            })
        elif state.risk_level == "Low":
            actions.append({
                "type": "notify_patient",
                "message": "Assistant: Thank you for your input. I have logged your status for the medical team."
            })
        else:
            actions.append({
                "type": "notify_patient",
                "message": "Assistant: Clinicians have been alerted. Please stay calm."
            })

        state.planned_actions = actions
        self.log(state, f"Planned {len(actions)} actions.")
        return state
