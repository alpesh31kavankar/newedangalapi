from app.services.ai_blog_agent import generate_daily_blogs
from app.database import SessionLocal


def run_ai_blog_agent():
    db = SessionLocal()
    try:
        generate_daily_blogs(db)
    finally:
        db.close()