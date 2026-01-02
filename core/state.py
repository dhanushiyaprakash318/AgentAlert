from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class PatientState(BaseModel):
    """
    Represents the unified state of a patient encounter as it flows through the agentic system.
    """
    session_id: str
    timestamp: datetime = Field(default_factory=datetime.now)
    
    # Input Data
    audio_path: Optional[str] = None
    transcript: Optional[str] = None
    
    # Extracted Info
    symptoms: List[str] = Field(default_factory=list)
    intent: Optional[str] = None
    patient_demographics: Dict[str, Any] = Field(default_factory=dict)
    
    # Reasoning & Risk
    risk_level: str = "Low"  # Low, Moderate, High, Critical
    reasoning: Optional[str] = None
    alerts_triggered: List[str] = Field(default_factory=list)
    
    # Decisions & Actions
    planned_actions: List[Dict[str, Any]] = Field(default_factory=list)
    executed_actions: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Feedback & Observation
    response_text: Optional[str] = None
    observations: List[str] = Field(default_factory=list)
    human_in_the_loop_required: bool = False
    
    # History
    agent_logs: List[Dict[str, Any]] = Field(default_factory=list)

    def add_log(self, agent_name: str, message: str):
        self.agent_logs.append({
            "timestamp": datetime.now().isoformat(),
            "agent": agent_name,
            "message": message
        })

    def to_dict(self):
        return self.model_dump()
