from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.blog import Blog
from app.schemas.blog import BlogCreate, BlogResponse

router = APIRouter(prefix="/blogs", tags=["Blogs"])


# ➜ Create Blog
@router.post("/", response_model=BlogResponse)
def create_blog(blog: BlogCreate, db: Session = Depends(get_db)):
    new_blog = Blog(**blog.dict())
    db.add(new_blog)
    db.commit()
    db.refresh(new_blog)
    return new_blog


# # ➜ Get All Blogs
# @router.get("/", response_model=list[BlogResponse])
# def get_blogs(db: Session = Depends(get_db)):
#     return db.query(Blog).all()
@router.get("/", response_model=list[BlogResponse])
def get_blogs(db: Session = Depends(get_db)):
    return db.query(Blog)\
        .filter(Blog.is_published == True)\
        .order_by(Blog.created_at.desc())\
        .all()

@router.get("/{slug}", response_model=BlogResponse)
def get_blog(slug: str, db: Session = Depends(get_db)):
    return db.query(Blog).filter(Blog.slug == slug).first()
