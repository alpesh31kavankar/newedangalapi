from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler

from app.database import Base, engine, get_db
from fastapi.staticfiles import StaticFiles
import os
import pprint
from fastapi.routing import APIRoute
routes_info = []

# ------------------------------
# Import all models so SQLAlchemy knows about tables and foreign keys
# ------------------------------
from app.models.category import Category
from app.models.product import Product
from app.models.question import Question
from app.models.question_round import QuestionRound
from app.models.email_verification import EmailVerification

# ------------------------------
# Import routers
# ------------------------------
from app.routes import categories, products, gifts, users, question_round ,email_verification ,auth, users_me,votes,tokens,daily_rewards,forgot_password,p_gift
# from .routes import forgot_password
from .routes import leaderboard
from app.routes.spin_routes import router as spin_router
from app.routes import lottery_result
from app.routes import reward_claim
from app.routes import review




from app.services.leaderboard_rank_updater import start_leaderboard_scheduler
from app.routes import results
# from app.routes import auth
# from app.routes import tokens
# ------------------------------
# Import cron function
# ------------------------------
from app.services.rounds_cron import generate_question_rounds
from app.services.finalize_rounds_cron import finalize_rounds
from app.services.lottery_cron import perform_daily_lottery
from app.services.participant_lottery_cron import perform_daily_participant_lottery
# ------------------------------
# Create all tables (SQLAlchemy will only create missing tables)
# ------------------------------
Base.metadata.create_all(bind=engine)
UPLOAD_DIR = "uploads/profile_images"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ------------------------------
# Initialize FastAPI
# ------------------------------
app = FastAPI()

app.mount("/uploads/profile_images", StaticFiles(directory=UPLOAD_DIR), name="profile_images")

# CORS configuration
origins = [
    "http://localhost:4200",
    "http://127.0.0.1:4200"
]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
# app.include_router(question_round_router.router)
app.include_router(categories.router)
app.include_router(products.router)
app.include_router(gifts.router)
app.include_router(p_gift.router)
app.include_router(question_round.router)
app.include_router(email_verification.router)
app.include_router(auth.router)
app.include_router(users_me.router)
app.include_router(users.router)
app.include_router(votes.router)
app.include_router(tokens.router)
app.include_router(results.router)
app.include_router(daily_rewards.router)
app.include_router(forgot_password.router)
app.include_router(leaderboard)
app.include_router(spin_router)
app.include_router(lottery_result.router)
app.include_router(reward_claim.router)
app.include_router(review.router)

print(app.routes)
for route in app.routes:
    if isinstance(route, APIRoute):  # only real HTTP routes, no mounts
        routes_info.append((route.path, route.methods))

pprint.pprint(routes_info)
# ------------------------------
# Scheduler setup for cron job
# ------------------------------
scheduler = BackgroundScheduler()

@app.on_event("startup")
def startup_event():
    # Schedule generate_question_rounds to run every 1 minute
    scheduler.add_job(generate_question_rounds, "interval", minutes=1)
    scheduler.add_job(finalize_rounds, "interval", minutes=1)
      # new job: run daily lottery at 20:00 (8 PM server time)
    scheduler.add_job(perform_daily_lottery, "cron", hour=18, minute=51)
    scheduler.add_job(
    perform_daily_participant_lottery,
    trigger="cron",
    hour=19,
    minute=6,
    id="participant_lottery_cron",
    replace_existing=True,
)
    start_leaderboard_scheduler()
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

