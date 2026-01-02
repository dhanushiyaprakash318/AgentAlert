try:
    import ollama
except ImportError:
    ollama = None
from core.base import BaseAgent
from core.state import PatientState

class ReasonerAgent(BaseAgent):
    """
    LLM-based reasoning for patient risk assessment.
    STRICT CONSTRAINTS: NO diagnosis, NO treatment suggestions.
    """
    def __init__(self, model_name: str = "llama3"):
        super().__init__("ReasonerAgent")
        self.model_name = model_name

    async def process(self, state: PatientState) -> PatientState:
        if not state.symptoms and not state.transcript:
            self.log(state, "No symptoms or transcript to reason about.")
            state.risk_level = "Low"
            return state

        prompt = f"""
        TASK: Assess patient risk level based on the following input.
        CONSTRAINTS: 
        - DO NOT provide medical diagnosis.
        - DO NOT suggest medications or treatments.
        - ONLY categorise the RISK LEVEL as: Low, Moderate, High, or Critical.
        - PROVIDE a brief technical justification for the risk level.

        PATIENT DATA:
        Transcript: "{state.transcript}"
        Detected Symptoms: {", ".join(state.symptoms)}

        OUTPUT FORMAT:
        Risk Level: [Low/Moderate/High/Critical]
        Reasoning: [Explanation]
        """

        try:
            if ollama is None:
                raise ImportError("Ollama library missing")
            
            self.log(state, f"Involving {self.model_name} for risk reasoning...")
            response = ollama.generate(model=self.model_name, prompt=prompt)
            output = response['response']
            
            # Basic parsing of the LLM output
            if "Risk Level:" in output:
                risk_part = output.split("Risk Level:")[1].split("\n")[0].strip().capitalize()
                for level in ["Low", "Moderate", "High", "Critical"]:
                    if level in risk_part:
                        state.risk_level = level
                        break
            
            if "Reasoning:" in output:
                state.reasoning = output.split("Reasoning:")[1].strip()
            else:
                state.reasoning = output.strip()

            self.log(state, f"Reasoning Complete. Risk Level: {state.risk_level}")
        
        except Exception as e:
            self.log(state, f"Ollama connection error: {str(e)}. Falling back to rule-based safety.")
            # Safety fallback
            if "chest pain" in state.symptoms or "difficulty breathing" in state.symptoms:
                state.risk_level = "Critical"
                state.reasoning = "Rule-based fallback: High-risk symptoms detected."
            else:
                state.risk_level = "Moderate" if state.symptoms else "Low"
                state.reasoning = "Rule-based fallback used."

        return state
