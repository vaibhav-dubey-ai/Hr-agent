# Full-Stack Architecture

## Final Folder Structure

```
hack/
├── backend/                          # FastAPI server
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                  # FastAPI app entry
│   │   ├── config.py                # Environment config
│   │   ├── schemas.py               # Pydantic models
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   ├── ranking.py           # POST /rank
│   │   │   ├── leave.py             # POST /leave
│   │   │   ├── scheduling.py        # POST /schedule
│   │   │   ├── pipeline.py          # POST /transition
│   │   │   ├── questions.py         # POST /generate-questions
│   │   │   └── export.py            # GET /export
│   │   └── core/
│   │       └── hr_agent.py          # Bridge to Python HR Agent
│   ├── requirements.txt
│   ├── .env
│   └── run.sh
│
├── frontend/                         # Next.js app
│   ├── app/
│   │   ├── layout.tsx               # Root layout
│   │   ├── page.tsx                 # Dashboard
│   │   ├── dashboard/
│   │   │   └── page.tsx             # Dashboard overview
│   │   ├── ranking/
│   │   │   └── page.tsx             # Resume ranking
│   │   ├── leave/
│   │   │   └── page.tsx             # Leave management
│   │   ├── scheduling/
│   │   │   └── page.tsx             # Interview scheduling
│   │   ├── pipeline/
│   │   │   └── page.tsx             # Candidate pipeline
│   │   └── api/
│   │       └── client.ts            # API client
│   ├── components/
│   │   ├── Navigation.tsx           # Header/nav
│   │   ├── Sidebar.tsx              # Left sidebar
│   │   ├── StatsCard.tsx            # Dashboard stat card
│   │   ├── CandidateTable.tsx       # Ranking table
│   │   ├── RankingModal.tsx         # Explanation modal
│   │   ├── LeaveForm.tsx            # Leave request form
│   │   ├── SchedulingForm.tsx       # Interview form
│   │   ├── PipelineVisualization.tsx # FSM diagram
│   │   └── Toast.tsx                # Notifications
│   ├── styles/
│   │   └── globals.css              # Global styles
│   ├── package.json
│   ├── tsconfig.json
│   ├── next.config.js
│   ├── tailwind.config.js
│   ├── .env.local
│   └── run.sh
│
├── hr_agent/                        # Existing Python modules
│   └── (all existing files)
│
├── docker-compose.yml               # Run both services
├── README.md                        # Full setup guide
└── run_all.sh                       # One-command startup

```

## Technology Stack

**Backend**:
- FastAPI (async REST API)
- Pydantic (data validation)
- Python 3.13
- CORS enabled
- Error handling middleware

**Frontend**:
- Next.js 14 (React)
- TypeScript
- Tailwind CSS
- SWR (data fetching)
- Dark mode support

**Integration**:
- REST API
- JSON payloads
- Environment variables
- Error boundaries

## API Endpoints

```
POST   /api/rank                 Rank resumes against JD
POST   /api/leave                Approve/reject leave
POST   /api/schedule             Schedule interview
POST   /api/transition           Move candidate in pipeline
POST   /api/generate-questions   Generate interview questions
GET    /api/export               Export all results
GET    /health                   Health check
```

## Frontend Pages

```
/                     Dashboard (stats + overview)
/dashboard            Same as above
/ranking              Resume ranking interface
/leave                Leave management
/scheduling           Interview scheduling
/pipeline             Candidate pipeline visualization
```

## Database

No database - all in-memory with session-based state. Can be extended with PostgreSQL.
