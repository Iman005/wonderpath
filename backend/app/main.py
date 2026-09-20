"""
WanderPath API entrypoint.

Wires together: CORS, the global exception handler (translates domain
exceptions into the standard JSON error shape — never a bare 500 for
known failure modes), and every module's router.
"""
import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.core.database import Base, SessionLocal, engine, ensure_sqlite_dev_columns
from app.infrastructure.data.seed import seed_iran_destinations
from app.modules.auth.router import router as auth_router
from app.modules.budget.router import router as budget_router
from app.modules.destination.router import router as destination_router
from app.modules.map.router import router as map_router
from app.modules.notebook.router import router as notebook_router
from app.modules.share.router import router as share_router
from app.modules.stay.router import router as stay_router
from app.modules.summary.router import router as summary_router
from app.modules.trip.router import trip_days_router, trips_router
from app.modules.weather.router import router as weather_router
from app.shared.exceptions import (
    DomainError,
    ExternalProviderError,
    NotFoundError,
    OwnershipError,
    UnauthorizedError,
    ValidationDomainError,
)
from app.shared.schemas import ErrorResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("wanderpath")

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    description="Trip planner & local guide for domestic travel inside Iran.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_origin_regex=settings.CORS_ORIGIN_REGEX or None,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Global exception handling (section 10 of the spec) ---

@app.exception_handler(NotFoundError)
async def not_found_handler(request: Request, exc: NotFoundError):
    return JSONResponse(status_code=404, content=ErrorResponse(error="not_found", message=exc.message).model_dump())


@app.exception_handler(OwnershipError)
async def ownership_handler(request: Request, exc: OwnershipError):
    return JSONResponse(status_code=403, content=ErrorResponse(error="ownership_mismatch", message=exc.message).model_dump())


@app.exception_handler(UnauthorizedError)
async def unauthorized_handler(request: Request, exc: UnauthorizedError):
    return JSONResponse(status_code=401, content=ErrorResponse(error="unauthorized", message=exc.message).model_dump())


@app.exception_handler(ValidationDomainError)
async def validation_handler(request: Request, exc: ValidationDomainError):
    return JSONResponse(status_code=422, content=ErrorResponse(error="validation_error", message=exc.message).model_dump())


@app.exception_handler(ExternalProviderError)
async def external_provider_handler(request: Request, exc: ExternalProviderError):
    # Graceful fallback, not a 500 — the frontend can show "map/place data
    # temporarily unavailable" instead of a generic crash.
    logger.error("External provider failure: %s", exc.message)
    return JSONResponse(
        status_code=503,
        content=ErrorResponse(error="external_provider_unavailable", message=exc.message).model_dump(),
    )


@app.exception_handler(DomainError)
async def domain_error_handler(request: Request, exc: DomainError):
    return JSONResponse(status_code=400, content=ErrorResponse(error="domain_error", message=exc.message).model_dump())


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(error="internal_error", message="An unexpected error occurred.").model_dump(),
    )


# --- Routers ---
app.include_router(auth_router)
app.include_router(destination_router)
app.include_router(trips_router)
app.include_router(trip_days_router)
app.include_router(budget_router)
app.include_router(stay_router)
app.include_router(notebook_router)
app.include_router(map_router)
app.include_router(summary_router)
app.include_router(weather_router)
app.include_router(share_router)


@app.get("/health", tags=["System"])
def health_check():
    return {"status": "ok"}


@app.on_event("startup")
def on_startup():
    # Local SQLite (and Fly volume SQLite) create tables here. Postgres uses Alembic.
    if settings.ENV == "development" or settings.DATABASE_URL.startswith("sqlite"):
        Base.metadata.create_all(bind=engine)
        ensure_sqlite_dev_columns()
    db = SessionLocal()
    try:
        cities, places = seed_iran_destinations(db)
        if cities or places:
            logger.info("Seeded %s cities and %s places.", cities, places)
    except Exception:
        logger.exception("Failed to seed Iran gazetteer")
    finally:
        db.close()
