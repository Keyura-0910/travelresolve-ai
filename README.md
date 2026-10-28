# TravelResolve — Booking-Aware Multi-Agent Support Automation

**Author:** [Keyura Motegaonkar](https://github.com/Keyura-0910)  
**Role:** Aspiring AI Engineer  

[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-StateGraph-orange.svg)](https://langchain-ai.github.io/langgraph/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> An auditable, booking-aware support automation system that classifies, prioritizes, investigates, and drafts resolutions for travel support tickets using classical machine learning, retrieval-augmented generation (RAG), and stateful LangGraph workflows. Developed by **Keyura Motegaonkar**.

---

## Problem Statement

Travel companies receive tens of thousands of customer support inquiries regarding booking confirmations, cancellations, refunds, hotel details, payment issues, and itinerary modifications. 

Generic AI chatbots often fail in production because:
1. **Lack of Booking Awareness**: They answer queries without verifying actual database records, promising refunds on non-refundable tickets or confirming cancellations that never took place.
2. **Policy Hallucinations**: They fabricate refund timeframes, fee waivers, or hotel amenities absent from official company policies.
3. **No Human-in-the-Loop Oversight**: Sensitive actions (financial refunds, medical emergency exceptions, high-value disputes) are either blocked or executed without supervisor authorization.
4. **No Verifiable Audit Trail**: Customer support operations require immutable traces for compliance, chargeback disputes, and managerial review.

**TravelResolve AI** solves this by uniting classical machine learning, retrieval-augmented generation (RAG), controlled database lookup tools, and a deterministic **Resolution Auditor** within a stateful **LangGraph DAG**. Sensitive, uncertain, or policy-violating tickets are automatically routed to a **Human Review Queue**.

> ⚠️ **Disclaimer**: This is an educational portfolio prototype operating on synthetic travel data. It does not integrate with real-world global distribution systems (GDS), airline reservation systems, or production hotel payment gateways.

---

## 🏗️ Architecture Overview

```
                                [ Customer Ticket Request ]
                                             │
                                             ▼
                               ┌───────────────────────────┐
                               │ 1. Intake & Classification│ ◄── Scikit-Learn (TF-IDF + LogReg)
                               └─────────────┬─────────────┘
                                             │
                                             ▼
                               ┌───────────────────────────┐
                               │ 2. Booking Investigation  │ ◄── Controlled SQLite Lookup Tool
                               └─────────────┬─────────────┘
                                             │
                                             ▼
                               ┌───────────────────────────┐
                               │  3. Knowledge Retrieval   │ ◄── FAISS / Lexical Fallback RAG
                               └─────────────┬─────────────┘
                                             │
                                             ▼
                               ┌───────────────────────────┐
                               │  4. Resolution Drafting   │ ◄── Hosted LLM / Deterministic Engine
                               └─────────────┬─────────────┘
                                             │
                                             ▼
                               ┌───────────────────────────┐
                               │   5. Resolution Auditor   │ ◄── Deterministic Verification Engine
                               └─────────────┬─────────────┘
                                             │
                                             ▼
                               ┌───────────────────────────┐
                               │    6. Routing Decision    │
                               └──────┬─────────────┬──────┘
                                      │             │
                [ Violations / Exceptions ]   [ Clean / Validated ]
                                      │             │
                                      ▼             │
                        ┌─────────────────────────┐ │
                        │  7. Human Review Queue  │ │
                        └─────────────┬───────────┘ │
                                      │             │
                                      ▼             ▼
                               ┌───────────────────────────┐
                               │      8. Finalization      │ ◄── SQLite Persistence & Audit Log
                               └───────────────────────────┘
```

---

## 🚀 Key Features

- **Classical ML Intent Classifier**: Trained with Scikit-learn (TF-IDF + Logistic Regression) on synthetic travel utterances across 6 intents (`booking_confirmation`, `cancellation`, `refund`, `booking_modification`, `payment_issue`, `general_travel_query`). Returns probability distributions and confidence scores.
- **Transparent Rule-Based Priority Engine**: Scores inquiries (0–100) based on time-to-checkin, VIP loyalty tier (Platinum/Gold), payment failure risk, and intent severity. Explains every score with plain-English reasons.
- **Controlled Booking Lookup Tools**: Isolated SQLite queries prevent cross-customer data leakage and completely prevent LLM fabrication of reservations.
- **Travel Policy RAG Pipeline**: Chunks and indexes 8 synthetic markdown policies into local FAISS vector store with fallback to lexical BM25 matching when external embedding APIs are absent.
- **Resolution Auditor**: Automatically cross-examines drafted responses against verified database records. Flags hallucinated booking IDs, contradictory dates, false cancellation claims, and unauthorized refunds on non-refundable fares.
- **LangGraph Stateful Agent Workflow**: Implements an 8-node directed acyclic graph with conditional branching, execution traces, and checkpointer persistence for human-in-the-loop workflow resumption.
- **Resolution Quality Lab (Benchmarking)**: Evaluates 100+ synthetic test cases comparing **Baseline** (Prompt only), **RAG Baseline** (Context only), and **TravelResolve AI** (Full LangGraph Workflow).
- **Dual Interfaces**: Full-featured **Streamlit UI** (7 dedicated views) and **FastAPI REST API** with interactive OpenAPI documentation.
- **Brand Identity & Vector Assets**: Custom TravelResolve logo system with 4 vector SVG assets (`primary_logo.svg`, `compact_logo.svg`, `icon_only.svg`, `monochrome_logo.svg`) uniting location pin, route swoosh, AI sparkle, and forward progress chevron.
- **Animated Transit Corridor**: Real-time CSS/SVG vehicle animations (curved flight path with rotating airplane, highway transit line with stylized car, and pulsing route checkpoints).

---

## 🎨 Brand Identity & Logo Assets

The TravelResolve logo unites four core design concepts:
1. **Travel Location Pin**: Anchors the platform in physical destinations and lodging.
2. **Curved Travel Route**: Sweeping orbital arc communicating journey and progress.
3. **AI Sparkle Core**: Central neural diamond node representing automated intelligence.
4. **Ascending Chevron**: Forward flight vector symbolizing resolution and problem-solving.

| Asset File | Purpose & Dimensions | Location |
|---|---|---|
| `primary_logo.svg` | Main horizontal logo with wordmark (290x64) | `app/ui/assets/primary_logo.svg` |
| `compact_logo.svg` | Sidebar navigation logo (230x48) | `app/ui/assets/compact_logo.svg` |
| `icon_only.svg` | Standalone icon mark & browser favicon (64x64) | `app/ui/assets/icon_only.svg` |
| `monochrome_logo.svg` | High-contrast single-color silhouette (64x64) | `app/ui/assets/monochrome_logo.svg` |

---

## 🛠️ Technology Stack

| Layer | Technologies |
|---|---|
| **Core Frameworks** | Python 3.11+, LangGraph, LangChain Core |
| **Machine Learning** | Scikit-learn, Pandas, NumPy, Joblib |
| **Vector Store & RAG** | FAISS CPU (`faiss-cpu`), Recursive Character Chunking |
| **Backend & Validation** | FastAPI, Pydantic v2, Pydantic Settings, SQLAlchemy |
| **Database** | SQLite (Single local file with WAL support) |
| **Frontend UI** | Streamlit (Inter + JetBrains Mono Design System) |
| **Testing & Quality** | Pytest, Pytest-Asyncio |
| **Containerization** | Docker, Docker Compose |

---

## ⚡ Quick Start Guide

### 1. Prerequisites
- Python 3.11+ installed.

### 2. Installation
```powershell
# Clone or navigate to the repository
cd C:\Users\Shilpa\.gemini\antigravity\scratch\travelresolve-ai

# Create and activate virtual environment (optional if global Python is configured)
python -m venv .venv
.venv\Scripts\Activate.ps1

# Install required dependencies
pip install -r requirements.txt
```

### 3. Initialize Synthetic Data and Models
Run the setup pipeline:
```powershell
# 1. Initialize SQLite database and seed synthetic bookings
python scripts/initialize_db.py

# 2. Train and evaluate the ML Intent Classifier
python scripts/train_model.py

# 3. Build the FAISS policy knowledge base
python scripts/build_knowledge_base.py

# 4. (Optional) Run the 100-case evaluation benchmark
python scripts/run_evaluation.py
```

### 4. Run Automated Tests
```powershell
pytest tests/ -v
```

### 5. Launch the Application

#### Option A: One-Command Development Launcher (Runs Both UI and Backend)
```powershell
python scripts/run_dev.py
```

#### Option B: Run Services in Separate Terminals
```powershell
# Terminal 1: FastAPI Backend
uvicorn app.api.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2: Streamlit Frontend
streamlit run app/ui/streamlit_app.py
```

- **Streamlit Web UI**: [http://localhost:8501](http://localhost:8501)
- **FastAPI OpenAPI Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Health Check**: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

---

## 📋 API Endpoints Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Service health status and version |
| `GET` | `/bookings` | List synthetic booking records |
| `GET` | `/bookings/{booking_id}` | Retrieve single booking record by ID |
| `POST` | `/tickets` | Submit customer inquiry and execute LangGraph workflow |
| `GET` | `/tickets` | List historical and active tickets |
| `GET` | `/tickets/{ticket_id}` | Retrieve ticket details, audit findings, and resolution |
| `GET` | `/tickets/{ticket_id}/trace`| Retrieve step-by-step LangGraph node execution trace |
| `GET` | `/tickets/{ticket_id}/audit`| Retrieve immutable audit logs for a ticket |
| `GET` | `/review-queue` | List tickets awaiting human supervisor approval |
| `POST` | `/tickets/{ticket_id}/review`| Submit supervisor review decision (`approve`, `reject`, `revise`) |
| `GET` | `/evaluation/metrics` | Retrieve cached 3-system benchmark metrics |
| `POST` | `/evaluation/run` | Execute on-demand 100-case evaluation benchmark |

---

## 🧪 Demonstration Walkthrough (For Interviews)

1. **Dashboard Page**: View total tickets, auto-resolution rate, audit pass rate, category breakdown, priority distribution, and live audit activity.
2. **Ticket Workspace**:
   - Select **Scenario 1 (Urgent Late Arrival)**: Shows imminent check-in (<24h) triggering Critical priority and auto-approval.
   - Select **Scenario 2 (Non-Refundable Emergency Cancellation)**: Demonstrates auditor detection of non-refundable status and automatic escalation to Human Review Queue.
   - Select **Scenario 5 (Missing Booking ID)**: Demonstrates handling nonexistent bookings without hallucinations.
3. **Bookings Directory**: Filter synthetic reservations across status, rate conditions (flexible vs non-refundable), customer loyalty tiers, and calculate real-time cancellation fees.
4. **Supervisor Review Queue**: Act as a supervisor, review escalated cases like `TCK-1002`, inspect reservation context and draft responses, and click **Approve**, **Edit & Approve**, or **Reject**.
5. **Execution Trace & Audit Log**: Inspect the chronological DAG state progression for any case with top workflow latency metrics, step-by-step human narrative summaries, clear status badges, and expandable JSON state payloads.
6. **Quality Lab**: Inspect Scikit-learn per-category precision/recall/F1 metrics, confusion matrix, deterministic auditor verification rules, and test arbitrary traveler messages in real-time in the interactive sandbox.
7. **Performance & Benchmarks**: Review the 3-system comparative benchmark (Prompt-Only Baseline vs RAG Baseline vs TravelResolve AI), latency profiling, and edge-case safety escalation recall (100% interception of sensitive risks).

---

## Security & Data Integrity Rules

1. **No External API Keys Required**: Runs with local deterministic template generation and dense vector FAISS index. If an `OPENAI_API_KEY` is provided in `.env`, the system automatically switches to hosted LLM inference.
2. **Untrusted Input Sanitation**: Customer messages and retrieved policy texts are treated as untrusted data. The auditor prevents prompt injections from authorizing unverified refunds.
3. **No Financial Side Effects**: Cancellation and refund amounts are computed for recommendation and approval, but real payment gateway actions are never executed.

---

**TravelResolve Operations Platform** • Developed by **Keyura Motegaonkar**
