from abc import ABC, abstractmethod
from core.state import PatientState

class BaseAgent(ABC):
    """
    Abstract Base Class for all agents in the system.
    """
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    async def process(self, state: PatientState) -> PatientState:
        """
        Process the current state and return the updated state.
        """
        pass

    def log(self, state: PatientState, message: str):
        print(f"[{self.name}] {message}")
        state.add_log(self.name, message)
