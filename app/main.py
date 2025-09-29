from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler

from app.database import Base, engine, get_db

# ------------------------------
# Import all models so SQLAlchemy knows about tables and foreign keys
# ------------------------------
from app.models.category import Category
from app.models.product import Product
from app.models.question import Question
from app.models.question_round import QuestionRound

# ------------------------------
# Import routers
# ------------------------------
from app.routes import categories, products, gifts, users, question_round

# ------------------------------
# Import cron function
# ------------------------------
from app.services.rounds_cron import generate_question_rounds

# ------------------------------
# Create all tables (SQLAlchemy will only create missing tables)
# ------------------------------
Base.metadata.create_all(bind=engine)

# ------------------------------
# Initialize FastAPI
# ------------------------------
app = FastAPI()

# CORS configuration
origins = [
    "http://localhost:4200",
    "http://127.0.0.1:4200"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
# app.include_router(question_round_router.router)
app.include_router(categories.router)
app.include_router(products.router)
app.include_router(gifts.router)
app.include_router(users.router)
app.include_router(question_round.router)
print(app.routes)

# ------------------------------
# Scheduler setup for cron job
# ------------------------------
scheduler = BackgroundScheduler()

@app.on_event("startup")
def startup_event():
    # Schedule generate_question_rounds to run every 1 minute
    scheduler.add_job(generate_question_rounds, "interval", minutes=100)
    scheduler.start()

@app.on_event("shutdown")
def shutdown_event():
    scheduler.shutdown()

# ------------------------------
# Root endpoint
# ------------------------------
@app.get("/")
def read_root():
    return {"message": "Welcome to Edangal API 🚀"}

