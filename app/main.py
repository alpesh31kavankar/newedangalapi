from fastapi import FastAPI
from app.database import Base, engine
from app import routes
from fastapi.middleware.cors import CORSMiddleware
# Create tables (if not using Alembic yet)
Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = [
    "http://localhost:4200",
    "http://127.0.0.1:4200"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # or ["*"] to allow all
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes.categories.router)
app.include_router(routes.products.router) 
app.include_router(routes.gifts.router) 
app.include_router(routes.users.router) 
# app.include_router(gifts_router)

# 
@app.get("/")
def read_root():
    return {"message": "Welcome to Edangal API 🚀"}



# from app.routes import products,categories,gifts
# app.include_router(categories.router)
# app.include_router(products.router) 
# app.include_router(gifts.router) 
