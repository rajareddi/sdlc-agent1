# 🌀 SDLC Agent (with Human-in-the-Loop)

This project demonstrates an **AI-powered Software Development Life
Cycle (SDLC) Agent** built using:

-   ⚡ **LangGraph** -- Orchestrator + Worker model\
-   ⚙️ **FastAPI** -- Backend service for agent execution\
-   🎨 **React + Tailwind + shadcn/ui** -- Frontend wizard UI\
-   👨‍💻 **Human-in-the-Loop (HITL)** -- User reviews and approves each
    SDLC step

------------------------------------------------------------------------

## 📖 Overview

The **SDLC Agent** automates the **six phases of software development**:

1.  **Planning** -- Generate project goals, scope, and resources.\
2.  **Analysis** -- Analyze requirements and constraints.\
3.  **Design** -- Create architecture, database schema, and UI mockups.\
4.  **Implementation** -- Generate code snippets or pseudocode.\
5.  **Testing** -- Propose QA strategies and test cases.\
6.  **Maintenance** -- Explain post-deployment monitoring and updates.

At each phase:\
- The **AI generates a draft output + checklist**.\
- The **human user reviews, edits, and approves** the draft.\
- Only the **approved version** is stored and used for the next step.

------------------------------------------------------------------------

## 🏗 Project Structure

    sdlc-agent/
    │── backend/          # FastAPI + LangGraph Orchestrator & Workers
    │   ├── app.py        # Main backend service
    │
    │── frontend/         # React + Tailwind + shadcn UI
    │   ├── src/App.jsx   # Wizard UI with Human-in-the-Loop
    │
    │── README.md         # Documentation

------------------------------------------------------------------------

## ⚙️ Backend Setup (FastAPI + LangGraph)

1.  Create Python virtual env & install deps:

    ``` bash
    cd backend
    python -m venv .venv
    
    # Activate virtual environment
    .venv\Scripts\activate      # (Windows)
    source .venv/bin/activate   # (Linux/Mac)

    # Install all dependencies
    pip install -r requirements.txt
    ```

2.  Configure environment variables:
    
    Make sure your `.env` file has the OpenAI API key:
    ```
    OPENAI_API_KEY=your-openai-api-key-here
    ```

3.  Run the backend server:

    ``` bash
    uvicorn app:app --reload --port 8000
    ```
    
    Or use the quick start script (Windows):
    ``` powershell
    .\start.ps1
    ```

This exposes APIs like:
- `GET /` → Health check
- `GET /phases` → Get all SDLC phases  
- `POST /generate-draft` → Generate AI draft for a phase
- `POST /approve-draft` → Approve a draft

------------------------------------------------------------------------

## 🎨 Frontend Setup (React + Tailwind + shadcn)

1.  Setup frontend project:

    ``` bash
    cd frontend
    npm install
    npm run dev
    ```

2.  Access UI at:

        http://localhost:5173

------------------------------------------------------------------------

## 🚀 Workflow

1.  User clicks **"Run Step"** → AI generates draft output for that SDLC
    phase.\
2.  Draft appears in a **textarea** → user can **edit and refine**.\
3.  User clicks **"Approve"** → marks it as final.\
4.  Only after approval, **"Next"** button is enabled.\
5.  Continue until **all 6 steps are approved**.\
6.  End result: a **human-validated SDLC Document**.

------------------------------------------------------------------------

## ✅ Features

-   🔄 **Orchestrator-Worker pattern** (LangGraph)\
-   👨‍💻 **Human-in-the-Loop review & approval**\
-   🖥 **Step-by-step wizard UI**\
-   📊 **Progress bar for SDLC phases**\
-   📦 Modular backend (FastAPI) + frontend (React)

------------------------------------------------------------------------

## 📌 Next Steps

-   [ ] Add **export to PDF/DOCX** feature for final SDLC report.\
-   [ ] Add **collaboration mode** (multiple reviewers).\
-   [ ] Integrate with **Jira/GitHub** for real project handoff.

------------------------------------------------------------------------

## 🏆 Example Output (Planning Phase)

    **Phase: Planning**

    **Draft Output**
    - Project Goals: Build a scalable e-commerce platform for small businesses.
    - Scope: User registration, product catalog, cart, checkout, payments.
    - Timeline: 6 months (2 months design, 2 months implementation, 1 month testing, 1 month buffer).
    - Resources: 5 developers, 1 QA, 1 DevOps, 1 Product Owner.
    - Risks & Mitigation: Delays → Agile sprints; Budget overrun → phased rollout.

    **Checklist for Human Review**
    - Are the goals aligned with business needs?
    - Is the scope realistic and sufficient?
    - Do the resources match project size?
