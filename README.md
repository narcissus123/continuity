# continuity
# Continuity Agent – Capstone Project
**Track:** Concierge Agents  
**Course:** 5-Day AI Agents Intensive (Google, Nov 2025)  
**Author:** Narges Haeri  
**GitHub:** [Your Repo Link]

---

## Overview
Continuity Agent is an AI-driven system designed to streamline and automate video creation workflows. Users can generate scene-based videos with character consistency, approve content in manageable batches, and seamlessly resume work across sessions. The agent demonstrates multi-agent orchestration, stateful session management, custom tools, and real-time user preference capture.  

This project applies learnings from the 5-Day AI Agents Intensive, including multi-agent design, tool integration, memory and session management, and prompt engineering for image generation.

---

## Problem Statement
Creating high-quality, consistent videos is typically manual, repetitive, and time-intensive. Users struggle to:
- Maintain character and style consistency across multiple scenes
- Manage iterative approvals efficiently
- Resume work across sessions without losing progress
- Control cost and generation time when using image generation models

**Goal:** Build an agent that automates video generation while preserving style, improving workflow efficiency, and maintaining flexibility for user corrections.

---

## Solution
The Continuity Agent leverages a **multi-agent system** to guide users from authentication to video creation, approvals, and session continuation.

Key features:
1. **Authentication**
   - Email-based registration for demonstration
   - Agent state holds user auth status
   - Plans for production: Firebase/Auth0 with email verification and JWT sessions

2. **Video & Scene Management**
   - Users can start new videos or continue existing ones
   - Scene generation in batches with user approval checkpoints
   - CLIP-based image consistency scoring to ensure quality

3. **Memory & Session Management**
   - Preferences and character references saved immediately
   - Only approved scenes stored to optimize cost and memory
   - Agent state reconstruction allows seamless session recovery

4. **Tools & Custom Logic**
   - `video_tools.py` for business logic and agent interactions
   - Image approval, batch generation, and style preview
   - Database access encapsulated in `database/models.py`

5. **Scalable Architecture**
   - **Database:** SQLite (dev) → PostgreSQL (production) for relational data
   - **Image storage:** Local for now; can move to cloud storage later
   - **Image comparison:** CLIP for on-the-fly matching; optional ChromaDB for future scaling

6. **Image Generation**
   - FLUX.1 Kontext Dev → Pro
   - Same prompt understanding across models
   - Model-specific CLIP thresholds and dynamic calibration
   - Generation timeout and cost management strategies

7. **User Workflow**
   - Users provide natural prompts: “Continue my dragon video” or “Start new video”
   - Menu displayed for new users or when requested
   - LLM interprets user intent to open or pause sessions

---

## Architecture
continuity/
├── database/
│ ├── init.py
│ ├── connection.py # DB connection
│ └── models.py # Users, Videos, Scenes
├── services/
│ └── video_service.py # Business logic
├── tools/
│ └── video_tools.py # Agent-accessible tools
└── agents/
├── root_agent.py # Orchestrates user sessions
├── greeting_agent.py # Handles authentication
├── menu_agent.py # Menu and task routing
└── video_agent.py # Video creation workflow

yaml
Copy code

**Agent Flow:**
1. `root_agent` orchestrates user flow.
2. `greeting_agent` handles authentication and email verification.
3. `menu_agent` guides users in task selection.
4. `video_agent` handles video generation, batch approvals, and memory persistence.

---

## Features Implemented
- Multi-agent system with sequential and parallel agents
- Custom tools for DB access, video generation, image approval
- Memory and session management with reconstruction for crashed sessions
- Prompt engineering for character consistency in images
- CLIP-based validation with model-specific thresholds
- Cost-aware batch processing

---

## Setup Instructions
1. Clone repository:
```bash
git clone https://github.com/<your-username>/continuity-agent.git
cd continuity-agent
Install dependencies:

bash
Copy code
pip install -r requirements.txt
Run agent locally using ADK-Python (Gemini 2.0 Flash model):

bash
Copy code
python agents/root_agent.py
Follow prompts in terminal / ADK web UI.

Type menu to see options anytime.

Provide natural prompts to continue existing sessions.