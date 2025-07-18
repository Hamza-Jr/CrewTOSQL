
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging
from fastapi import FastAPI
from src.initializer import complete_crew  # your Crew setup


# Import your existing crew
from src.initializer import complete_crew

# Configure logging 
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Student SQL Crew API",
    description="AI-powered natural language to SQL query system for student transcript data",
    version="1.0.0",
)


class QueryRequest(BaseModel):
    query: str


# Allow frontend access (for Streamlit)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/query")
def handle_query(request: QueryRequest):
    try:
        result = complete_crew.kickoff(inputs={"user_query": request.query.strip()})
        return result.raw
    except Exception as e:
        return {"error": str(e)}

