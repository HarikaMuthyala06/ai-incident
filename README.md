# AI Incident Investigation & Postmortem Agent

A complete, full-stack AI Site Reliability Engineering (SRE) platform designed to investigate production software incidents across diverse applications (E-commerce, Ride-Booking, College Portals, Core Banking, Chat Applications, Delivery Services), retrieve troubleshooting runbooks using a manual RAG pipeline and vector search, formulate evidence-based root-cause hypotheses, and generate structured blameless postmortem reports.

---

## 🚀 Live on Localhost

Both services are active on your machine:

- **Frontend Application:** [http://localhost:5173](http://localhost:5173)
- **FastAPI Backend API:** [http://localhost:8000](http://localhost:8000)
- **Interactive API Documentation (Swagger):** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Health Telemetry Endpoint:** [http://localhost:8000/api/health](http://localhost:8000/api/health)

---

## 🧠 Educational Core: Understanding the AI & RAG Pipeline

As a Computer Science student, this project avoids hiding mechanics behind heavy abstractions like LangChain. Here is how each stage works under the hood:

### 1. Document Ingestion & Text Extraction
- **PyMuPDF (`fitz`)**: Extracts text stream from PDF documents.
- **`python-docx`**: Parses paragraphs and runs from Word documents.
- **Normal Text / Log Parsers**: Cleans raw `.txt`, `.log`, and Markdown files.

### 2. Overlapping Sliding Window Chunking
- Documents are split into semantic chunks (default ~700 characters) with **150-character overlap**.
- **Why overlap?** Overlapping prevents critical error signatures or diagnostic commands from being split right at a chunk boundary, preserving contextual coherence.

### 3. Dense Vector Embeddings
- Text chunks are mapped into high-dimensional vectors (1,536 dimensions) using OpenAI's `text-embedding-3-small`.
- If running offline without an API key, an in-engine normalized semantic frequency vector fallback is computed so learning and testing never break.

### 4. Vector Storage & Similarity Search
- **MongoDB Atlas Vector Search**: Uses the `$vectorSearch` aggregation stage with HNSW (Hierarchical Navigable Small World) indexing.
- **In-Engine Cosine Similarity Math**:
  $$\text{Cosine Similarity}(\vec{A}, \vec{B}) = \frac{\sum_{i=1}^n A_i B_i}{\sqrt{\sum_{i=1}^n A_i^2} \sqrt{\sum_{i=1}^n B_i^2}}$$
  Computes the angular distance between the incident query vector and all stored runbook chunk vectors, returning top-k matching guides with relevance scores (High $\ge 0.75$, Medium $\ge 0.50$, Low $< 0.50$).

### 5. Grounded LLM Prompting & Safety Guardrails
- **Root-Cause Hypothesis**: The AI agent is strictly instructed via system prompt to formulate a *probable cause hypothesis* rather than claiming false certainty.
- **Safety First**: The agent generates read-only investigation commands and rollback guidance, never executing dangerous mutating production commands.

---

## 🛠️ Tech Stack

- **Frontend:** React 18, Vite, Tailwind CSS v4, Lucide Icons, Recharts, Axios, React Router v7
- **Backend:** Python 3.14, FastAPI, Pydantic v2, Uvicorn, Motor (Async MongoDB Driver)
- **AI & RAG:** OpenAI API (`gpt-4o-mini`, `text-embedding-3-small`), PyMuPDF, python-docx, NumPy
- **Auth:** JWT (JSON Web Tokens), Bcrypt password hashing
- **Database:** MongoDB Atlas (with automatic local in-memory fallback)

---

## 🧪 6x6 Incident Simulator

The built-in simulator allows you to test 36 realistic production failure scenarios across 6 industry domains:

| Application Domain | Supported Failure Scenarios |
|---|---|
| **E-commerce** | Database Connection Pool Exhaustion, Payment Gateway 504 Timeouts, Session Expirations, Search Latency, Container OOMKilled, Inventory gRPC Deadlines |
| **Ride Booking** | Driver Matching Service 503, Redis Geospatial Outages, Wallet Lock Contention, Real-Time WebSockets Lag |
| **College Portal** | Hall-Ticket Spike & Unindexed Database Table Scans, Student SSO LDAP Timeout |
| **Banking** | Expired RSA Signing Certificate / JWT Rejections, Account Balance Ledger Deadlocks |
| **Chat Application** | RabbitMQ Queue Congestion & Async Worker Starvation, Message Stuck in "Sending" |
| **Delivery Application** | GeoIP Library Shared Object Mismatch on Container Startup, Driver Route Latency |

---

## 💻 How to Run Locally

### Start Backend:
```powershell
cd "e:\AI Project\backend"
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### Start Frontend:
```powershell
cd "e:\AI Project\frontend"
npm run dev
```

---

## 🔑 Environment Configuration (`backend/.env`)

```env
PORT=8000
ENVIRONMENT=development
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

SECRET_KEY=incident-investigator-super-secret-key-32charsmin!
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# MongoDB (Atlas connection string or local MongoDB):
MONGODB_URI=mongodb://localhost:27017
DATABASE_NAME=incident_agent_db

# OpenAI API (Optional for GPT-4o / text-embedding-3-small; platform includes offline SRE heuristic fallback):
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
```

---

## 👤 Default Demo Accounts

Click the **Sign In** button in the top navigation bar to use 1-click credentials:
- **On-Call SRE Engineer:** `engineer` / `engineer123`
- **SRE Lead Admin:** `admin` / `admin123`

