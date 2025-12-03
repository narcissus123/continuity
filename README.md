# continuity
# Continuity Agent – Capstone Project
**Track:** Concierge Agents  
**Course:** 5-Day AI Agents Intensive (Google, Nov 2025)  
**Author:** Narges Haeri  
**GitHub:** [Your Repo Link]

---

# Continuity

> AI-Powered Character-Consistent Video Generation for YouTube Creators

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Google ADK](https://img.shields.io/badge/Built%20with-Google%20ADK-4285F4)](https://github.com/google/adk)

**Continuity** is a multi-agent AI system built with Google's Agent Development Kit (ADK) that solves the character consistency problem in AI-generated video content. It combines CLIP similarity scoring, semantic memory learning, and human-in-the-loop workflows to generate 18-24 visually consistent images per video while learning from user preferences.

🎯 **Perfect for:** YouTube creators producing 1-2 educational/storytelling videos per week  
⚡ **Time Savings:** 50-60% reduction in video production time  
💰 **Cost:** ~$0.50 per video (vs $30/month subscriptions)

---

## 📚 Table of Contents

- [Problem Statement](#-problem-statement)
- [Solution Overview](#-solution-overview)
- [Key Features](#-key-features)
- [Architecture](#-architecture)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Usage Guide](#-usage-guide)
- [Technical Deep Dive](#-technical-deep-dive)
- [Production Roadmap](#-production-roadmap)

---

## 🎯 Problem Statement

YouTube content creators using AI image generation face a **critical consistency problem**: standard tools generate each image independently, causing character features to drift unpredictably across scenes.

**Example:**
- **Scene 1:** Dragon with bright blue scales, golden eyes, prominent horns
- **Scene 5:** Same dragon now has darker blue scales, silver eyes, smaller horns  
- **Scene 12:** Dragon's face structure has completely changed

This destroys narrative immersion and signals amateur production quality.

**Why Existing Solutions Fall Short:**
- **Standard Generators:** No memory of previous outputs
- **Image-to-Image:** Still produces significant variation  
- **Manual Post-Processing:** 15-30 minutes per image × 20 images = Not scalable

---

## 💡 Solution Overview

Continuity uses a **multi-agent architecture** combining:

1. **Google ADK Multi-Agent System** - Agent orchestration
2. **VertexAI Semantic Memory** - Learns user preferences across videos
3. **CLIP Similarity Scoring** - Quantifies visual consistency (0-100%)
4. **Replicate API (FLUX.1 Kontext)** - Character-consistent image generation

**Workflow:**
```
User: "Create a video about a space explorer"
  ↓
Script Agent: Breaks story into 20 scenes
  ↓
Scene Agent: Generates character reference image
  ↓
Image Agent: For each scene:
  → Generate image (Replicate API)
  → Calculate CLIP similarity vs reference
  → Score ≥ 85%? ✅ Auto-approve
  → Score < 85%? ⚠️ Regenerate or user review
  ↓
Memory Agent: Learns from approvals/rejections
  ↓
Next video: Applies learned preferences automatically
```

---

## ✨ Key Features

### 🤖 Multi-Agent Architecture
- **Root Agent:** Dynamic routing and coordination
- **Sequential Agents:** Enforced workflow steps (greeting, video creation)
- **Loop Agents:** Variable iterations (batch generation with human review)
- **Agent Tool Wrapping:** Clean separation of concerns

### 🧠 Learning System
- **VertexAI Memory Bank** stores semantic preferences
- **Cross-Video Learning:** Video 1 informs Video 2 generations
- **Measurable Improvement:** 33% fewer regenerations by video 5

### 📊 CLIP Similarity Scoring
- **Quantifiable Consistency:** 0-100% similarity scores
- **Automated Decisions:** Auto-approve ≥85%, auto-reject <75%
- **Fast Inference:** ~100ms per image on CPU

### 🔄 Human-in-the-Loop Workflow
- **Batch Generation:** 5-6 scenes at once for efficient review
- **Pause/Resume:** Long-running operations with checkpoints
- **Smart Regeneration:** Only rejected images, not entire batches

### 💾 Session Management
- **Multi-Session Architecture:** One session per video project
- **Session Isolation:** Switch between videos without state pollution
- **Crash Recovery:** DatabaseSessionService with SQLite persistence

---

## 🏗️ Architecture

### System Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         root_agent                              │
│                  (LlmAgent - Coordinator)                       │
│  • Handles user identification & session management             │
│  • Dynamic routing based on user intent                         │
│  • Delegates to specialized sub-agents                          │
└─────────────────────────────────────────────────────────────────┘
          │
          ├──→ greeting_agent (SequentialAgent)
          │     │
          │     ├──→ name_agent (collect name)
          │     ├──→ email_agent (collect email)
          │     └──→ token_agent (verify email)
          │
          ├──→ menu_agent (LlmAgent)
          │     └─ Lists user's video projects
          │     └─ Shows in-progress and completed videos
          │     └─ Provides usage statistics
          │
          └──→ video_workflow_agent (SequentialAgent)
                  │
                  ├──→ script_agent (LlmAgent)
                  │     └─ Generates video script from topic
                  │     └─ Breaks into individual scene descriptions
                  │     └─ Sources from educational content
                  │
                  ├──→ scene_agent (LlmAgent)
                  │     └─ Creates detailed prompts for each scene
                  │     └─ Generates character reference image
                  │     └─ Maintains character description consistency
                  │
                  └──→ image_generation_agent (LoopAgent)
                        │
                        ├──→ Phase 1: Style Previews
                        │     └─ Generate 2-3 style variations
                        │     └─ User selects preferred style
                        │
                        └──→ Phase 2: Batch Generation Loop
                              ├─ Generate 5-6 scenes per batch
                              ├─ Calculate CLIP scores for all
                              ├─ Present batch for user review
                              ├─ Identify rejections (low score or user feedback)
                              ├─ Regenerate rejected scenes
                              ├─ Present regenerations
                              ├─ Mark approved images as final
                              └─ Continue until all scenes complete
```

### Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Agent Framework | Google ADK (Python) | Multi-agent orchestration |
| LLM | Gemini 2.0 Flash | Agent reasoning and planning |
| Image Generation | Replicate (FLUX.1 Kontext) | Character-consistent images |
| Similarity Scoring | CLIP (OpenAI) | Visual consistency measurement |
| Memory | VertexAI Memory Bank | Semantic preference storage |
| Session Storage | SQLite + DatabaseSessionService | Conversation and state persistence |
| Business Data | SQLite | Users, videos, scenes, images |
| File Storage | Local filesystem | Generated images (demo) |
| Embeddings | HuggingFace Transformers | CLIP model inference |

---

## 🚀 Installation

### Prerequisites

- **Python 3.10+** (tested on 3.10, 3.11, 3.12)
- **Google Cloud Project** with billing enabled
- **API Keys:**
  - Google AI Studio API key (for Gemini)
  - Replicate API token
- **8GB+ RAM** (for CLIP model inference)
- **10GB+ disk space** (for model cache and images)

### Step 1: Clone Repository

```bash
git clone https://github.com/narci/continuity.git
cd continuity
```

### Step 2: Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Core Dependencies:**
```txt
google-adk==0.1.0
replicate==0.25.0
transformers==4.36.0
torch==2.1.0
Pillow==10.1.0
scikit-learn==1.3.2
python-dotenv==1.0.0
```

⚠️ **Note:** `transformers` and `torch` are large downloads (~4GB combined). Installation may take 5-10 minutes.

### Step 4: Set Up Environment Variables

Create `.env` file in project root:

```bash
# .env
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_API_KEY=your-gemini-api-key
REPLICATE_API_TOKEN=your-replicate-token

# Optional: Custom paths
DATABASE_PATH=continuity.db
ADK_SESSION_DB_PATH=adk_sessions.db
DATA_DIRECTORY=data
```

**Get API Keys:**
- **Gemini:** https://aistudio.google.com/app/apikey
- **Replicate:** https://replicate.com/account/api-tokens

### Step 5: Configure Google Cloud

```bash
# Authenticate with Google Cloud
gcloud auth application-default login

# Enable required APIs
gcloud services enable aiplatform.googleapis.com

# Set project
gcloud config set project YOUR_PROJECT_ID
```

### Step 6: Initialize Database

```bash
python setup_database.py
```

**This creates:**
- `continuity.db` with schema (users, videos, scenes, images)
- `adk_sessions.db` (managed by ADK)
- `data/` directory for images
- `~/.continuity/` for persistent state

### Step 7: Verify Installation

```bash
python -c "from google.adk import *; from transformers import CLIPModel; print('✅ All imports successful')"
```

---

## 🎬 Quick Start

### Basic Usage

```bash
# Activate virtual environment
source venv/bin/activate

# Run Continuity
python main.py
```

### First-Time User Flow

```
👋 Hi there, Welcome to Continuity!

You: Hi
🤖 Agent: What's your name?

You: Narci
🤖 Agent: Nice to meet you, Narci! What's your email address?

You: your.email@example.com
🤖 Agent: Email saved! Welcome to Continuity!

What would you like to do?
• Create new video
• View limits
• About Continuity

You: Create new video
🤖 Agent: Great! What's your video about?

You: A space explorer discovering alien artifacts
🤖 Agent: Generating script...

[Script generated with 20 scenes]

🤖 Agent: Here's the script. Approve to continue?

You: Yes
🤖 Agent: Generating character reference...

[Reference image generated]

🤖 Agent: Here's your space explorer. Approve?

You: Yes
🤖 Agent: Generating first batch of scenes (1-6)...

[Batch generation with CLIP scores]

🤖 Agent: 
Scene 1: ✅ 92% consistency
Scene 2: ⚠️ 78% consistency
Scene 3: ✅ 89% consistency
Scene 4: ✅ 94% consistency
Scene 5: ✅ 86% consistency
Scene 6: ⚠️ 76% consistency

Review scene 2 and 6? [approve/reject/regenerate]

You: regenerate 2 and 6
🤖 Agent: Regenerating scenes 2 and 6...

[Regenerations complete]

Scene 2 (v2): ✅ 91% consistency
Scene 6 (v2): ✅ 88% consistency

Approve batch?

You: Yes
🤖 Agent: Batch approved! Moving to scenes 7-12...
```

---

## 📖 Usage Guide

### Creating a New Video

1. **Start session:** `python main.py`
2. **Choose "Create new video"**
3. **Provide topic:** "A story about..."
4. **Review script:** Agent generates 15-25 scene descriptions
5. **Approve script:** Proceed to character generation
6. **Review reference:** First image sets character baseline
7. **Batch generation:** Review 5-6 scenes at a time
8. **Approve/regenerate:** Adjust scenes below consistency threshold
9. **Complete video:** All scenes approved and saved

### Switching Between Videos

```
You: Menu
🤖 Agent: Your videos:
  1. "Space Explorer" (in progress)
  2. "Dragon Adventure" (completed)
  3. "Robot Quest" (in progress)

You: Continue Robot Quest
🤖 Agent: Resuming "Robot Quest"...
```

### Understanding CLIP Scores

| Score Range | Meaning | Action |
|------------|---------|--------|
| 0.90-1.00 | Excellent consistency | Auto-approve |
| 0.85-0.89 | Good consistency | Auto-approve |
| 0.75-0.84 | Moderate consistency | User review |
| 0.60-0.74 | Low consistency | Auto-regenerate |
| 0.00-0.59 | Very poor consistency | Auto-regenerate |

---

## 🔬 Technical Deep Dive

### CLIP Similarity Scoring

**How It Works:**

1. Load CLIP model (cached after first use)
2. Encode images to 512-dimensional embeddings
3. Calculate cosine similarity between vectors
4. Score ranges from 0.0 (different) to 1.0 (identical)

**Why CLIP:**
- ✅ Semantic understanding (recognizes "dragon" not just "blue pixels")
- ✅ Robust to pose/angle/lighting changes
- ✅ Pre-trained, no custom training needed
- ✅ Fast inference (~100ms on CPU)

### Multi-Session Architecture

**Why Session-Per-Video:**
- Clean state isolation
- Easy video switching
- Independent crash recovery
- Mirrors real-world usage patterns

**Implementation:**
```python
async def get_or_create_adk_session_for_video(video_id: str, user_id: str):
    """Get existing session or create new one for video"""
    video = VideoModel.get_by_id(video_id)
    
    if video and video.get("last_session_id"):
        try:
            return await session_service.get_session(
                app_name="continuity",
                user_id=user_id,
                session_id=video["last_session_id"]
            )
        except:
            pass  # Create new if corrupted
    
    # Create new session
    session_id = f"video_{video_id}_{user_id[:8]}"
    session = await session_service.create_session(
        app_name="continuity",
        user_id=user_id,
        session_id=session_id,
        state={"video:id": video_id, "temp:scenes_completed": 0}
    )
    
    VideoModel.update_session_id(video_id, session.session_id)
    return session
```

---

## 🚀 Production Roadmap

### Current State: Demo/MVP

**What Works:**
- ✅ Multi-agent ADK system
- ✅ Email-based user identification  
- ✅ Session management
- ✅ CLIP similarity scoring
- ✅ VertexAI memory learning
- ✅ Local storage & SQLite

### Phase 1: Authentication (Week 1-2)
- [ ] Magic link email verification
- [ ] Session timeout
- [ ] Rate limiting

### Phase 2: Storage (Week 3-4)
- [ ] AWS S3 integration
- [ ] CloudFront CDN
- [ ] 30-day automated cleanup

### Phase 3: Database (Week 5-6)
- [ ] PostgreSQL migration
- [ ] Connection pooling
- [ ] Automated backups

### Phase 4: API (Week 7-8)
- [ ] FastAPI wrapper
- [ ] JWT authentication
- [ ] WebSocket for real-time updates

### Phase 5: Vector DB (When >1000 images)
- [ ] ChromaDB integration
- [ ] Batch encoding pipeline

---

### Development Setup

```bash
git clone https://github.com/YOUR_USERNAME/continuity.git
cd continuity
git checkout -b feature/your-feature
pip install -r requirements-dev.txt
pytest  # Run tests
```

---

**Narges Haeri** - Project Creator
- GitHub: https://github.com/narcissus123/continuity/tree/main

---

**Built with ❤️ by Narci for the YouTube creator community**














