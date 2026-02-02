# EduMesh OS

**Hackathon-Grade Agentic AI System** powered by **Gemini 3 Pro** (Simulated via Experimental Thinking Models).

## Overview
EduMesh OS is an autonomous system designed to optimize community learning ecosystems. It moves beyond simple "matching" to perform strategic **arbitrage** of skills and needs.

Using a graph-based memory (Neo4j) and high-level reasoning agents (Gemini), it identifies hidden opportunities, predicts skill gaps, and selects community leaders.

## Key Features

### 1. Persistent Thought Signature
Unlike standard chatbots, EduMesh agents maintain a "Thought Signature" across chain-of-thought interactions. This allows the system to build upon previous reasoning steps without losing context or hallucinating new constraints.

### 2. High-Reasoning Gap Detection
Where deterministic logic sees simple shortages (e.g., "Not enough Mentors"), the **Gap Detector Agent** sees structural arbitrage opportunities (e.g., "Person A knows X, Person B needs X, but they are separated by language Y - intervention required").

### 3. Resilience (Mock Mode)
The system strictly prioritizes uptime. If the Neo4j Graph Database is unreachable, the **Graph Core** automatically falls back to an in-memory NetworkX simulation, ensuring the demo never fails for the judges.

## Architecture

- **Backend**: Python 3.11, Google GenAI SDK
- **AI Core**: Gemini 2.0 Flash Thinking (Proxy for Gemini 3 Pro)
- **Database**: Neo4j (with NetworkX Fallback)
- **Frontend**: Streamlit
- **Agents**:
  - `EntityExtractor`: Sociographic Analysis
  - `GapDetector`: Strategic Reasoning
  - `LeadSelector`: Talent Scouting

## Usage

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Generate Data**
   ```bash
   python data/mock_data_generator.py
   ```

3. **Run System**
   ```bash
   streamlit run frontend/app.py
   ```

## Folder Structure (Locked)
- `backend/`: Core logic and Agents
- `data/`: Mock data generators
- `frontend/`: Streamlit UI
- `agents/`: Mission definitions

---
*Built for the Gemini 3 Pro Hackathon.*
