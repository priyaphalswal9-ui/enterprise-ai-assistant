from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.db.database import SessionLocal
from backend.app.services.evaluation_service import evaluate_rag
from backend.app.api.v1.auth import get_current_user


router = APIRouter(prefix="/evaluations", tags=["Evaluations"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/rag")
def run_rag_evaluation(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_id = int(current_user["sub"])

    return evaluate_rag(
        user_id=user_id,
        k=3,
    )
from pydantic import BaseModel

from backend.app.services.evaluation_service import evaluate_answer


class AnswerEvaluationRequest(BaseModel):
    question: str
    answer: str
    context: str


@router.post("/answer")
def run_answer_evaluation(
    request: AnswerEvaluationRequest,
):
    return evaluate_answer(
        question=request.question,
        answer=request.answer,
        context=request.context,
    )