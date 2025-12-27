from fastapi import FastAPI, HTTPException, Query, Security, status, Request
from fastapi.security import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.openapi.utils import get_openapi
from typing import List, Optional
from pydantic import BaseModel
from skills_data import job_skills, common_positions
from dotenv import load_dotenv
import uvicorn
import secrets
import os

# Load environment variables from .env file
load_dotenv()

app = FastAPI(
    title="Job Portal Skills API",
    description="API for retrieving job positions and their relevant skills (API Key Required)",
    version="1.0.0",
    docs_url=None,  # Disable default docs
    redoc_url=None,  # Disable default redoc
    openapi_url=None  # Disable default openapi
)

# API Key Configuration
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)

# Load API Keys from environment variables (comma-separated)
# For local development, use .env file
# For Vercel, set environment variables in dashboard
api_keys_env = os.getenv("API_KEYS")
if not api_keys_env:
    raise ValueError("API_KEYS environment variable is not set. Please configure it in your .env file or environment.")
VALID_API_KEYS = set(key.strip() for key in api_keys_env.split(",") if key.strip())

# Function to generate new API keys (for admin use)
def generate_api_key() -> str:
    """Generate a new secure API key"""
    return f"sk_{''.join(secrets.token_hex(16))}"

async def verify_api_key(api_key: str = Security(api_key_header)) -> str:
    """Verify the API key from request headers"""
    if api_key in VALID_API_KEYS:
        return api_key
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing API Key. Please provide a valid API key in the X-API-Key header."
    )

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Response Models
class SkillsResponse(BaseModel):
    position: str
    skills: List[str]
    skills_count: int


class PositionsResponse(BaseModel):
    positions: List[str]
    total_count: int


class PositionSuggestionsResponse(BaseModel):
    suggestions: List[str]
    query: str


class JobCategoryResponse(BaseModel):
    category: str
    positions: List[str]


class AllJobsResponse(BaseModel):
    categories: dict
    total_positions: int


@app.get("/", tags=["Root"])
async def root():
    """Welcome endpoint with API information (No API key required)"""
    return {
        "message": "Welcome to Job Portal Skills API",
        "version": "1.0.0",
        "authentication": "API Key required in X-API-Key header",
        "endpoints": {
            "positions": "/api/positions",
            "skills": "/api/skills/{position}",
            "suggestions": "/api/suggestions",
            "categories": "/api/categories",
            "all_jobs": "/api/all-jobs"
        },
        "documentation": {
            "swagger": "/docs (requires API key)",
            "redoc": "/redoc (requires API key)"
        }
    }


# Protected Documentation Endpoints
@app.get("/docs", include_in_schema=False)
async def get_documentation(api_key: str = Security(verify_api_key)):
    """Swagger UI documentation (API Key Required)"""
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title=f"{app.title} - Swagger UI"
    )


@app.get("/redoc", include_in_schema=False)
async def get_redoc_documentation(api_key: str = Security(verify_api_key)):
    """ReDoc documentation (API Key Required)"""
    return get_redoc_html(
        openapi_url="/openapi.json",
        title=f"{app.title} - ReDoc"
    )


@app.get("/openapi.json", include_in_schema=False)
async def get_open_api_endpoint(api_key: str = Security(verify_api_key)):
    """OpenAPI schema (API Key Required)"""
    return get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )


@app.get("/api/positions", response_model=PositionsResponse, tags=["Positions"])
async def get_all_positions(api_key: str = Security(verify_api_key)):
    """Get all available job positions (API Key Required)"""
    return {
        "positions": common_positions,
        "total_count": len(common_positions)
    }


@app.get("/api/skills/{position}", response_model=SkillsResponse, tags=["Skills"])
async def get_skills_for_position(position: str, api_key: str = Security(verify_api_key)):
    """
    Get relevant skills for a specific job position (API Key Required)

    - **position**: Job position name (case-insensitive)
    """
    normalized_position = position.lower().strip()

    # Try exact match first
    if normalized_position in job_skills:
        skills = job_skills[normalized_position]
        return {
            "position": position,
            "skills": skills,
            "skills_count": len(skills)
        }

    # Try partial match
    for key, skills in job_skills.items():
        if normalized_position in key or key in normalized_position:
            return {
                "position": position,
                "skills": skills,
                "skills_count": len(skills)
            }

    raise HTTPException(
        status_code=404,
        detail=f"No skills found for position: {position}. Try /api/positions to see available positions."
    )


@app.get("/api/suggestions", response_model=PositionSuggestionsResponse, tags=["Positions"])
async def get_position_suggestions(
    q: str = Query(..., min_length=1, description="Search query for job position"),
    api_key: str = Security(verify_api_key)
):
    """
    Get job position suggestions based on search query (API Key Required)

    - **q**: Search query (minimum 1 character)
    """
    if not q.strip():
        return {
            "suggestions": [],
            "query": q
        }

    lower_query = q.lower()
    suggestions = [
        position for position in common_positions
        if lower_query in position.lower()
    ][:10]  # Limit to top 10 matches

    return {
        "suggestions": suggestions,
        "query": q
    }


@app.get("/api/categories", response_model=List[JobCategoryResponse], tags=["Categories"])
async def get_job_categories(api_key: str = Security(verify_api_key)):
    """Get all job positions organized by categories (API Key Required)"""
    categories = {
        "Software Development": [
            "Software Developer",
            "Software Engineer",
            "Full Stack Developer",
            "Frontend Developer",
            "Backend Developer",
            "Mobile Developer",
        ],
        "Data & AI": [
            "Data Scientist",
            "Data Analyst",
            "Data Engineer",
            "Machine Learning Engineer",
            "AI Engineer",
        ],
        "DevOps & Cloud": [
            "DevOps Engineer",
            "Cloud Engineer",
            "System Administrator",
            "Network Engineer",
            "Database Administrator",
        ],
        "Design": [
            "UI/UX Designer",
            "Graphic Designer",
            "Web Designer",
        ],
        "Management": [
            "Product Manager",
            "Project Manager",
            "Scrum Master",
        ],
        "Quality Assurance": [
            "Quality Assurance Engineer",
            "QA Tester",
        ],
        "Security": [
            "Security Engineer",
        ],
        "Business": [
            "Business Analyst",
            "Marketing Manager",
            "Sales Manager",
            "Customer Success Manager",
            "HR Manager",
            "Financial Analyst",
            "Accountant",
        ],
        "Content & Marketing": [
            "Technical Writer",
            "Content Writer",
            "SEO Specialist",
            "Digital Marketing Specialist",
        ],
    }

    return [
        {"category": category, "positions": positions}
        for category, positions in categories.items()
    ]


@app.get("/api/all-jobs", response_model=AllJobsResponse, tags=["Categories"])
async def get_all_jobs_with_skills(api_key: str = Security(verify_api_key)):
    """Get all job positions with their skills organized by categories (API Key Required)"""
    categories = {
        "Software Development": {},
        "Data & AI": {},
        "DevOps & Cloud": {},
        "Design": {},
        "Management": {},
        "Quality Assurance": {},
        "Security": {},
        "Business": {},
        "Content & Marketing": {},
    }

    category_mapping = {
        "Software Development": [
            "software developer", "software engineer", "full stack developer",
            "frontend developer", "backend developer", "mobile developer"
        ],
        "Data & AI": [
            "data scientist", "data analyst", "data engineer",
            "machine learning engineer", "ai engineer"
        ],
        "DevOps & Cloud": [
            "devops engineer", "cloud engineer", "system administrator",
            "network engineer", "database administrator"
        ],
        "Design": [
            "ui/ux designer", "graphic designer", "web designer"
        ],
        "Management": [
            "product manager", "project manager", "scrum master"
        ],
        "Quality Assurance": [
            "quality assurance engineer", "qa tester", "qa engineer"
        ],
        "Security": [
            "security engineer"
        ],
        "Business": [
            "business analyst", "marketing manager", "sales manager",
            "customer success manager", "hr manager", "financial analyst", "accountant"
        ],
        "Content & Marketing": [
            "technical writer", "content writer", "seo specialist",
            "digital marketing specialist"
        ],
    }

    for category, positions in category_mapping.items():
        for position in positions:
            if position in job_skills:
                categories[category][position] = job_skills[position]

    return {
        "categories": categories,
        "total_positions": len(job_skills)
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Job Portal Skills API"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
