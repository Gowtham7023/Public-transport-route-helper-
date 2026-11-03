import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.database.connection import init_db
from app.services.transport_data_service import TransportDataService
from app.services.gazetteer_service import GazetteerService
from app.services.india_transit_seeder import seed_india_wide_transit
from app.api import stations, routes, ai, predictions, data, health, places

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("transit_helper")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup sequence
    logger.info("Starting Public Transport Route Helper for India API...")
    init_db()

    # Seed Indian places gazetteer and verified multimodal transit data
    try:
        gaz = GazetteerService()
        gaz.seed_places_if_empty()
        gaz.close()

        svc = TransportDataService()
        svc.seed_initial_verified_data()
        svc.close()

        seed_india_wide_transit()
    except Exception as e:
        logger.warning(f"Notice during startup data seeding: {e}")

    logger.info("System ready to serve India-wide route planning requests.")
    yield
    # Shutdown sequence
    logger.info("Shutting down API services.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=(
        "Production-grade multimodal public transport journey planner for India. "
        "Combines NetworkX Graph routing algorithms, Scikit-learn Machine Learning "
        "for train-delay prediction, and Google Gemini Generative AI for natural "
        "language query understanding and route reasoning."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permits local frontend dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Exception Handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error processing {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred while processing the transit request.", "error": str(exc)}
    )

# Include Routers
app.include_router(health.router)
app.include_router(places.router)
app.include_router(stations.router)
app.include_router(routes.router)
app.include_router(ai.router)
app.include_router(predictions.router)
app.include_router(data.router)

@app.get("/")
def root():
    return {
        "name": settings.PROJECT_NAME,
        "version": "2.0.0",
        "platform": "India-Wide Multimodal Transit Network",
        "documentation": "/docs",
        "status": "ONLINE"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)

