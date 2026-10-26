import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from api.crud_routes import router as crud_router
from api.remarks_routes import router as remarks_router
from migrations.runner import run_migrations

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("health-backend")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Execute database migrations automatically upon application startup
    logger.info("Initializing application and executing startup migrations...")
    try:
        run_migrations()
        logger.info("Database migrations successfully checked and applied.")
    except Exception as exc:
        logger.error(f"Migration runner failed during startup: {exc}", exc_info=True)
        raise exc
    yield
    logger.info("Shutting down application...")


app = FastAPI(
    title="Health Prediction & Patient Management API",
    description="Clean, modular REST API for patient health tracking and biomarker assessment.",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure Cross-Origin Resource Sharing (CORS) for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers with /api prefix
app.include_router(crud_router, prefix="/api")
app.include_router(remarks_router, prefix="/api")


@app.get("/", tags=["Health"])
def root():
    return {
        "status": "healthy",
        "service": "Health Prediction & Patient Management API",
        "version": "1.0.0",
        "endpoints": {
            "docs": "/docs",
            "patients": "/api/patients",
            "preview_remarks": "/api/remarks/preview",
        },
    }


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
