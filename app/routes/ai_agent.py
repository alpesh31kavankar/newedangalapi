from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.ai_blog_agent import generate_daily_blogs

router = APIRouter(prefix="/ai-agent", tags=["AI Agent"])


@router.post("/generate-blogs")
def run_agent(db: Session = Depends(get_db)):
    generate_daily_blogs(db)
    return {"message": "Blogs generated successfully"}