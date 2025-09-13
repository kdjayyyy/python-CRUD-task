import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.employees import router as employees_router
from app.db import mongo_client, ensure_indexes_and_collections, mongo_client as client_wrapper
from app.config import settings

# basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Assessment API",
    description="FastAPI scaffold for assessment (Phase A).",
    version="0.1.0",
)


# allow CORS for local testing (adjust origins in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    # connect to MongoDB
    try:
        await mongo_client.connect()
    except Exception as exc:
        logger.exception("Could not connect to MongoDB on startup: %s", exc)
        # rethrow to fail startup so user notices
        raise

    # ensure collection + indexes
    db = mongo_client.get_database()
    await ensure_indexes_and_collections(db)
    logger.info("Startup complete")


@app.on_event("shutdown")
async def shutdown():
    await mongo_client.close()
    logger.info("Shutdown complete")


@app.get("/", tags=["health"])
async def root():
    return {"status": "ok", "service": "assessment_api"}


# include routers
app.include_router(employees_router, prefix="/employees", tags=["employees"])
