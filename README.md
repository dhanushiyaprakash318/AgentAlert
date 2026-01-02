# AgentAlert: Patient Risk Detection & Alerting Framework

A production-ready agentic AI framework for hospital environments, designed to monitor patient vocalizations and trigger intelligent alerts.

## 🚀 Overview
AgentAlert uses a multi-agent orchestration pattern to process patient inputs (voice/text), assess risk levels without providing medical diagnoses, and execute deterministic safety actions.

### 🏗️ Agent Pipeline
1.  **Listener Agent**: Converts audio to text using **Whisper**.
2.  **Detector Agent**: Extracts symptoms and patient intent using advanced pattern matching.
3.  **Reasoner Agent**: Leverages **LLaMA (via Ollama)** for deep reasoning about risk based on symptoms.
4.  **Planner Agent**: Applies rule-based logic to decide on necessary actions (Alert staff, notify patient).
5.  **Executor Agent**: Executes side effects (Console alerts, simulated notifications).
6.  **Feedback Agent**: Observes the final state, ensures safety overrides, and logs the audit trail.

## 🏃 Running the System
### Real-Time Voice Mode (Continuous Monitoring)
The system will listen to your microphone, process speech, and respond via synthesized voice.
```bash
python main.py
```

### Tech Stack (Updated)
- **Python 3.10+**
- **Whisper**: Speech-to-Text
- **Ollama (LLaMA 3)**: Reasoning Engine
- **sounddevice**: Real-time Audio Capture
- **pyttsx3**: Text-to-Speech (Voice Response)

## ⚠️ Safety & Constraints
-   **No Diagnosis**: The system identifies risk levels (Low, Moderate, High, Critical) but never names a disease.
-   **Rule-based Planning**: Final decisions are made by deterministic rules, not purely by the LLM, ensuring safety.
-   **Human-in-the-Loop**: High-risk scenarios always trigger a staff alert.
