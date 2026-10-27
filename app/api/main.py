"""
FastAPI application entry point for TravelResolve AI.
Configures CORS, database initialization, route mounting, and OpenAPI metadata.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db, SessionLocal
from app.seed_data import generate_seed_data
from app.database import Booking
from app.api.routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle startup handler: ensures database tables exist and seeds data if empty."""
    init_db()
    with SessionLocal() as db:
        booking_count = db.query(Booking).count()
        if booking_count == 0:
            print("Database is empty. Populating initial synthetic seed data...")
            generate_seed_data(db)
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "Auditable, booking-aware multi-agent travel support automation system "
        "powered by LangGraph, Scikit-Learn ML, RAG, and deterministic verification."
    ),
    lifespan=lifespan
)

# Cross-Origin Request configuration for local Streamlit UI and tools
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routes
app.include_router(router, prefix="/api/v1")
app.include_router(router)  # Direct root alias for convenience


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.api.main:app", host=settings.API_HOST, port=settings.API_PORT, reload=True)
