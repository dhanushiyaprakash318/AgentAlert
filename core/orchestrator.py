from typing import List
from core.base import BaseAgent
from core.state import PatientState
from agents.detector import DetectorAgent
from agents.reasoner import ReasonerAgent
from agents.planner import PlannerAgent
from agents.executor import ExecutorAgent
from agents.feedback import FeedbackAgent

class HospitalOrchestrator:
    """
    Orchestrates the flow of agents for patient risk detection.
    """
    def __init__(self, ollama_model: str = "llama3"):
        self.agents: List[BaseAgent] = [
            DetectorAgent(),
            ReasonerAgent(model_name=ollama_model),
            PlannerAgent(),
            ExecutorAgent(),
            FeedbackAgent()
        ]

    async def run_pipeline(self, state: PatientState, on_agent_complete=None) -> PatientState:
        print(f"\n--- Starting Orchestration for Session {state.session_id} ---")
        for agent in self.agents:
            state = await agent.process(state)
            if on_agent_complete:
                await on_agent_complete(agent.name, state)
        print(f"--- Orchestration Complete for Session {state.session_id} ---\n")
        return state
