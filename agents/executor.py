import time
from core.base import BaseAgent
from core.state import PatientState

class ExecutorAgent(BaseAgent):
    """
    Executes the deterministic actions planned by the PlannerAgent.
    In a real system, this would call APIs, send SMS, or trigger alarms.
    """
    def __init__(self):
        super().__init__("ExecutorAgent")

    async def process(self, state: PatientState) -> PatientState:
        if not state.planned_actions:
            self.log(state, "No actions to execute.")
            return state

        for action in state.planned_actions:
            action_type = action.get("type")
            self.log(state, f"Executing: {action_type}...")
            
            # Simulate side effects
            if action_type == "alert_staff":
                self._send_staff_alert(action)
            elif action_type == "notify_patient":
                self._send_patient_notification(action)
                state.response_text = action.get("message")
            
            # Record execution
            executed = action.copy()
            executed["status"] = "success"
            executed["executed_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
            state.executed_actions.append(executed)

        self.log(state, f"Successfully executed {len(state.executed_actions)} actions.")
        return state

    def _send_staff_alert(self, action):
        # Placeholder for actual alerting service (e.g., PagerDuty, Twilio, Hospital Dashboard)
        print(f">>> [SYSTEM ALERT] Target: {action['target']} | Priority: {action['priority']} | Message: {action['message']}")

    def _send_patient_notification(self, action):
        # Placeholder for Text-to-Speech or Voice Response
        print(f">>> [PATIENT MESSAGE] {action['message']}")
