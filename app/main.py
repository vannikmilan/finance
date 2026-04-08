from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine
from . import models

from .routers import users, settings, months, balances, summary

# Create tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="MyWorth API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all our split-up routes
app.include_router(users.router)
app.include_router(settings.router)
app.include_router(months.router)
app.include_router(balances.router)
app.include_router(summary.router)