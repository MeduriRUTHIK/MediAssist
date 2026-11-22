
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from app.routes.chat import router as chat_router

# Initialize FastAPI
app = FastAPI(
    title="MediAssist API",
    description="AI-powered Medical Information Assistant",
    version="1.0.0"
)

# CORS configuration for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000"
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register chatbot routes
app.include_router(chat_router)


# Home endpoint
@app.get("/")
def home():
    return {
        "message": "Welcome to MediAssist!",
        "status": "running"
    }


# Health check endpoint
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "application": "MediAssist"
    }
