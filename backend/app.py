from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import os
from dotenv import load_dotenv
import logging
import httpx

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables FIRST before importing opik
import pathlib
env_path = pathlib.Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path, override=True)

# Configure Opik environment variables BEFORE importing opik
# This ensures Opik reads the correct URL on initialization
OPIK_URL = os.getenv("OPIK_URL_OVERRIDE", "http://192.168.1.5:5173/api")
OPIK_PROJECT = os.getenv("OPIK_PROJECT_NAME", "sdlc-agent")
OPIK_WORKSPACE = os.getenv("OPIK_WORKSPACE", "default")

os.environ["OPIK_URL_OVERRIDE"] = OPIK_URL
os.environ["OPIK_PROJECT_NAME"] = OPIK_PROJECT
os.environ["OPIK_WORKSPACE"] = OPIK_WORKSPACE

# Print Opik configuration
print("=" * 60)
print("OPIK CONFIGURATION:")
print(f"  OPIK_URL_OVERRIDE: {OPIK_URL}")
print(f"  OPIK_PROJECT_NAME: {OPIK_PROJECT}")
print(f"  OPIK_WORKSPACE: {OPIK_WORKSPACE}")
print("=" * 60)

# Monkey-patch httpx to log all requests
_original_httpx_request = httpx.Client.request
_original_httpx_async_request = httpx.AsyncClient.request

def _logged_request(self, method, url, **kwargs):
    print("\n" + "=" * 60)
    print("OPIK HTTP REQUEST DEBUG:")
    print(f"  METHOD: {method}")
    print(f"  URL: {url}")
    print(f"  HEADERS: {kwargs.get('headers', {})}")
    if 'json' in kwargs:
        import json
        print(f"  BODY (JSON): {json.dumps(kwargs['json'], indent=2)[:2000]}")
    if 'content' in kwargs:
        print(f"  BODY (CONTENT): {str(kwargs['content'])[:2000]}")
    print("=" * 60 + "\n")

    response = _original_httpx_request(self, method, url, **kwargs)

    print("\n" + "=" * 60)
    print("OPIK HTTP RESPONSE DEBUG:")
    print(f"  STATUS CODE: {response.status_code}")
    print(f"  HEADERS: {dict(response.headers)}")
    print(f"  BODY: {response.text[:1000] if response.text else 'empty'}")
    print("=" * 60 + "\n")

    return response

async def _logged_async_request(self, method, url, **kwargs):
    print("\n" + "=" * 60)
    print("OPIK ASYNC HTTP REQUEST DEBUG:")
    print(f"  METHOD: {method}")
    print(f"  URL: {url}")
    print(f"  HEADERS: {kwargs.get('headers', {})}")
    if 'json' in kwargs:
        import json
        print(f"  BODY (JSON): {json.dumps(kwargs['json'], indent=2)[:2000]}")
    if 'content' in kwargs:
        print(f"  BODY (CONTENT): {str(kwargs['content'])[:2000]}")
    print("=" * 60 + "\n")

    response = await _original_httpx_async_request(self, method, url, **kwargs)

    print("\n" + "=" * 60)
    print("OPIK ASYNC HTTP RESPONSE DEBUG:")
    print(f"  STATUS CODE: {response.status_code}")
    print(f"  HEADERS: {dict(response.headers)}")
    print(f"  BODY: {response.text[:1000] if response.text else 'empty'}")
    print("=" * 60 + "\n")

    return response

httpx.Client.request = _logged_request
httpx.AsyncClient.request = _logged_async_request

# Now import opik after environment variables are set
import opik
from opik.integrations.langchain import OpikTracer

from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langchain_core.messages import SystemMessage

# Configure Opik client with use_local=True and IP address
opik.configure(use_local=True)

# Create OpikTracer for LangChain integration
opik_tracer = OpikTracer(
    project_name=OPIK_PROJECT,
    tags=["sdlc-agent", "langgraph", "openrouter"]
)

app = FastAPI(title="SDLC Agent API", description="AI-powered SDLC with LangGraph Orchestrator")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY environment variable is required")
llm = ChatOpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1",
    model="openai/gpt-4o",
    temperature=0.7,
    callbacks=[opik_tracer]  # Add Opik tracer as callback
)



SDLC_PHASES = [
    "Planning",
    "Analysis", 
    "Design",
    "Implementation",
    "Testing",
    "Maintenance"
]

# State model for LangGraph
class SDLCState(BaseModel):
    phase: str
    project_context: str = ""
    draft_output: str = ""
    checklist: list = []
    approved: bool = False
    error: Optional[str] = None

# Request/Response models
class GenerateDraftRequest(BaseModel):
    phase: str
    project_context: str = ""

class ApproveDraftRequest(BaseModel):
    phase: str
    approved_content: str

# Worker functions for each SDLC phase
def planning_worker(state: Dict[str, Any]) -> Dict[str, Any]:
    """Worker for Planning phase"""
    try:
        prompt = f"""
        You are an expert project planner. Generate a comprehensive planning document for: {state['project_context']}
        
        Include:
        - Project Goals
        - Scope definition
        - Timeline estimates
        - Resource requirements
        - Risk assessment and mitigation strategies
        
        Format as structured text with clear sections.
        """

        messages = [SystemMessage(content=prompt)]
        response = llm.invoke(messages)

        checklist = [
            "Are the goals aligned with business needs?",
            "Is the scope realistic and sufficient?",
            "Do the resources match project size?",
            "Are risks properly identified and mitigated?"
        ]

        return {
            **state,
            "draft_output": response.content,
            "checklist": checklist,
            "error": None
        }
    except Exception as e:
        return {**state, "error": str(e)}

def analysis_worker(state: Dict[str, Any]) -> Dict[str, Any]:
    """Worker for Analysis phase"""
    try:
        prompt = f"""
        You are a business analyst. Based on the project context: {state['project_context']}
        
        Provide detailed analysis including:
        - Functional requirements
        - Non-functional requirements
        - User stories and use cases
        - System constraints
        - Acceptance criteria
        
        Format as structured requirements document.
        """

        messages = [SystemMessage(content=prompt)]
        response = llm.invoke(messages)

        checklist = [
            "Are requirements clear and measurable?",
            "Are constraints properly identified?",
            "Do user stories cover all scenarios?",
            "Are acceptance criteria well-defined?"
        ]

        return {
            **state,
            "draft_output": response.content,
            "checklist": checklist,
            "error": None
        }
    except Exception as e:
        return {**state, "error": str(e)}

def design_worker(state: Dict[str, Any]) -> Dict[str, Any]:
    """Worker for Design phase"""
    try:
        prompt = f"""
        You are a system architect. Based on the project: {state['project_context']}
        
        Create a comprehensive design including:
        - System architecture overview
        - Database schema design
        - API design and endpoints
        - UI/UX wireframes description
        - Technology stack recommendations
        - Security considerations
        
        Format as technical design document.
        """

        messages = [SystemMessage(content=prompt)]
        response = llm.invoke(messages)

        checklist = [
            "Is the architecture scalable and maintainable?",
            "Are security considerations addressed?",
            "Is the database design normalized?",
            "Are UI mockups user-friendly?"
        ]

        return {
            **state,
            "draft_output": response.content,
            "checklist": checklist,
            "error": None
        }
    except Exception as e:
        return {**state, "error": str(e)}

def implementation_worker(state: Dict[str, Any]) -> Dict[str, Any]:
    """Worker for Implementation phase"""
    try:
        prompt = f"""
        You are a senior developer. Based on the project: {state['project_context']}
        
        Provide implementation guidance including:
        - Code structure and organization
        - Key algorithms and logic
        - Database implementation details
        - API implementation examples
        - Frontend component structure
        - Development best practices
        
        Include code snippets where relevant.
        """

        messages = [SystemMessage(content=prompt)]
        response = llm.invoke(messages)

        checklist = [
            "Is code modular and reusable?",
            "Are best practices followed?",
            "Is error handling implemented?",
            "Are performance considerations addressed?"
        ]

        return {
            **state,
            "draft_output": response.content,
            "checklist": checklist,
            "error": None
        }
    except Exception as e:
        return {**state, "error": str(e)}

def testing_worker(state: Dict[str, Any]) -> Dict[str, Any]:
    """Worker for Testing phase"""
    try:
        prompt = f"""
        You are a QA engineer. For the project: {state['project_context']}
        
        Create a comprehensive testing strategy including:
        - Test plan and strategy
        - Unit test cases
        - Integration test scenarios
        - User acceptance test cases
        - Performance testing approach
        - Security testing considerations
        - Test automation recommendations
        
        Format as detailed testing document.
        """
        
        messages = [SystemMessage(content=prompt)]
        response = llm.invoke(messages)
        
        checklist = [
            "Are test cases comprehensive?",
            "Is the QA strategy robust?",
            "Are performance tests included?",
            "Is test automation considered?"
        ]
        
        return {
            **state,
            "draft_output": response.content,
            "checklist": checklist,
            "error": None
        }
    except Exception as e:
        return {**state, "error": str(e)}

def maintenance_worker(state: Dict[str, Any]) -> Dict[str, Any]:
    """Worker for Maintenance phase"""
    try:
        prompt = f"""
        You are a DevOps engineer. For the project: {state['project_context']}
        
        Create a maintenance and operations plan including:
        - Deployment strategy
        - Monitoring and alerting setup
        - Backup and recovery procedures
        - Performance optimization
        - Security updates and patches
        - Documentation and knowledge transfer
        - Support and maintenance procedures
        
        Format as operations manual.
        """
        
        messages = [SystemMessage(content=prompt)]
        response = llm.invoke(messages)
        
        checklist = [
            "Is monitoring properly set up?",
            "Are update procedures clear?",
            "Is backup strategy comprehensive?",
            "Are security measures in place?"
        ]
        
        return {
            **state,
            "draft_output": response.content,
            "checklist": checklist,
            "error": None
        }
    except Exception as e:
        return {**state, "error": str(e)}

# LangGraph orchestrator setup
def create_sdlc_graph():
    """Create the SDLC orchestrator graph"""
    
    def orchestrator(state: Dict[str, Any]) -> Dict[str, Any]:
        """Orchestrator that routes to appropriate worker based on phase"""
        phase = state.get("phase", "").lower()
        
        if phase == "planning":
            return planning_worker(state)
        elif phase == "analysis":
            return analysis_worker(state)
        elif phase == "design":
            return design_worker(state)
        elif phase == "implementation":
            return implementation_worker(state)
        elif phase == "testing":
            return testing_worker(state)
        elif phase == "maintenance":
            return maintenance_worker(state)
        else:
            return {**state, "error": f"Unknown phase: {phase}"}
    
    # Create the graph
    workflow = StateGraph(dict)
    workflow.add_node("orchestrator", orchestrator)
    workflow.set_entry_point("orchestrator")
    workflow.add_edge("orchestrator", END)
    
    return workflow.compile()

# Initialize the graph
sdlc_graph = create_sdlc_graph()

# API Endpoints
@app.get("/")
def root():
    return {"message": "SDLC Agent API with LangGraph Orchestrator", "status": "running"}

@app.get("/next-phase")
def next_phase(current: Optional[str] = None):
    """Returns the next SDLC phase after the current one"""
    if current is None:
        return {"next": SDLC_PHASES[0]}
    try:
        idx = SDLC_PHASES.index(current)
        if idx + 1 < len(SDLC_PHASES):
            return {"next": SDLC_PHASES[idx + 1]}
        else:
            return {"next": None, "message": "All phases completed."}
    except ValueError:
        return {"error": "Invalid phase name."}

@app.post("/generate-draft")
def generate_draft(request: GenerateDraftRequest):
    """Generate AI draft for a specific SDLC phase using LangGraph orchestrator"""
    if request.phase not in SDLC_PHASES:
        raise HTTPException(status_code=400, detail="Invalid phase name")
    
    # if not OPENAI_API_KEY or OPENAI_API_KEY == "your-openai-api-key-here":
    #     raise HTTPException(status_code=500, detail="OpenAI API key not configured")
    #
    try:
        # Create initial state
        initial_state = {
            "phase": request.phase,
            "project_context": request.project_context,
            "draft_output": "",
            "checklist": [],
            "approved": False,
            "error": None
        }
        
        # Run the LangGraph orchestrator
        result = sdlc_graph.invoke(initial_state)
        
        if result.get("error"):
            raise HTTPException(status_code=500, detail=result["error"])
        
        return {
            "phase": result["phase"],
            "draft_output": result["draft_output"],
            "checklist": result["checklist"],
            "status": "generated"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/approve-draft")
def approve_draft(request: ApproveDraftRequest):
    """Mark a draft as approved by the human reviewer"""
    if request.phase not in SDLC_PHASES:
        raise HTTPException(status_code=400, detail="Invalid phase name")
    
    # In a real implementation, you would store this in a database
    return {
        "phase": request.phase,
        "approved_content": request.approved_content,
        "status": "approved",
        "timestamp": "2025-08-31T04:00:00Z"
    }

@app.get("/phases")
def get_phases():
    """Get all available SDLC phases"""
    return {"phases": SDLC_PHASES}
