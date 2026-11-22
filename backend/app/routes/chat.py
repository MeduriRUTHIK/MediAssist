
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.gemini_service import generate_response

router = APIRouter(prefix="/api", tags=["Medical Chatbot"])


class ChatRequest(BaseModel):
    question: str


class ChatResponse(BaseModel):
    answer: str


EMERGENCY_KEYWORDS = [
    "heart hurts",
    "heart pain",
    "chest pain",
    "chest hurts",
    "chest pressure",
    "chest tightness",
    "difficulty breathing",
    "shortness of breath",
    "cannot breathe",
    "can't breathe",
    "unconscious",
    "severe bleeding",
    "stroke symptoms"
]


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):

    question = " ".join(request.question.lower().split())

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Please enter a question."
        )

    # Emergency detection BEFORE calling Gemini
    if any(keyword in question for keyword in EMERGENCY_KEYWORDS):

        print("EMERGENCY DETECTED - Gemini bypassed")

        return ChatResponse(
            answer=(
                "⚠️ POTENTIAL MEDICAL EMERGENCY\n\n"
                "Chest pain or heart-related discomfort can "
                "have serious causes.\n\n"
                "If this is happening now, seek immediate "
                "medical attention. In India, call 112 for "
                "emergency assistance.\n\n"
                "Do not drive yourself. Do not wait for an "
                "AI response.\n\n"
                "MediAssist cannot diagnose or rule out "
                "a medical emergency."
            )
        )

    # Normal questions go to Gemini
    try:
        answer = generate_response(request.question)

        return ChatResponse(answer=answer)

    except Exception as error:
        print(f"Gemini API Error: {error}")

        raise HTTPException(
            status_code=503,
            detail="AI service is temporarily unavailable. Please try again."
        )
