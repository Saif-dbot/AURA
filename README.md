# AURA

**AURA** (Advanced Universal Resume Architect & Analytics) is a local desktop platform designed to support industrial maintenance workflows. The application combines a modern desktop interface, local data persistence, document analysis, and a foundation for AI-assisted maintenance using RAG and a local LLM.

## Business Overview

AURA is built to help maintenance teams centralize operational information, reduce manual work, and improve decision-making. The current version focuses on:

- local desktop usage on Windows
- secure local authentication
- event and audit logging
- maintenance planning and technician scheduling
- document analysis and prompt-based maintenance assistance
- a dashboard-oriented interface with sidebar navigation
- a local SQLite database prepared for future growth

## Main Value for an Organization

AURA can help an enterprise by:

- reducing time spent searching for procedures and manuals
- structuring maintenance knowledge in one local tool
- improving traceability of actions and interventions
- providing a stable desktop experience for operational teams
- creating a path toward RAG-based assistance and AI-generated recommendations

## Current Features

- modern desktop interface with sidebar navigation
- login screen and local authentication
- KPI-style home dashboard
- event history and audit trail
- planning and scheduling views
- technical document loading and analysis
- multi-LLM support (Ollama, Mistral, Groq) for maintenance instruction generation
- local SQLite storage with versioned schema initialization

## Technology Stack

### Core
- Python 3.14
- Tkinter / ttk
- SQLite

### Data and Analytics
- pandas
- numpy
- matplotlib
- seaborn
- scikit-learn

### NLP and Document Processing
- spaCy
- sentence-transformers
- PyPDF2
- python-docx

### LLM Providers
- Ollama (local)
- Mistral API
- Groq API

### Reporting
- reportlab

## Project Structure

```text
AURA/
├── main.py
├── requirements.txt
├── ROADMAP_IMPROVEMENTS.md
├── README.md
├── data/
├── src/
│   ├── app_config.py
│   ├── app_logger.py
│   ├── auth_manager.py
│   ├── dashboards.py
│   ├── database/
│   ├── gui.py
│   ├── llm_service.py
│   ├── nlp_engine.py
│   ├── planning.py
│   ├── prompt_generator.py
│   ├── scheduling.py
│   ├── storage.py
│   └── theme.py
└── AURA_presentation.tex
```

## How to Run

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure optional environment variables

Create a `.env` file in the project root if needed:

```env
AURA_DB_PATH=data/aura.db
AURA_DB_FILENAME=aura.db

# Ollama (local)
OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_MODEL=llama3.1:8b

# Mistral API
MISTRAL_API_KEY=your_mistral_api_key

# Groq API
GROQ_API_KEY=your_groq_api_key
```

### 3. Launch the application

```bash
python main.py
```

## Default Access

The application creates a default local administrator account if no user exists:

- Username: `admin`
- Password: `admin123`

For security reasons, change this password before production use.

## Database and Persistence

AURA uses a local SQLite database to store:

- users
- events
- machines
- technicians
- interventions
- documents
- sensors

The schema is initialized automatically at startup through the local migration runner in `src/database/`.

## Roadmap

See [ROADMAP_IMPROVEMENTS.md](ROADMAP_IMPROVEMENTS.md) for the improvement plan. The current priorities are:

1. RAG for local manuals and reports
2. LLM-based maintenance assistance
3. richer CRUD operations for interventions and reports
4. stronger authentication and roles
5. packaging and enterprise deployment

## Notes for Enterprise Use

This project is currently suitable as a local prototype and internal operational tool. Before enterprise deployment, the following should be added or hardened:

- role-based access control
- secure secret management
- database backup strategy
- automated tests
- packaging and installer creation
- audit and compliance review
- RAG indexing pipeline for documents
