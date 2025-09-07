import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api import characters, health, images, stories
from config.settings import settings

# Import test endpoints only in development
if settings.environment == "development":
    from api import test_endpoints

# Configure logging
logging.basicConfig(
    level=logging.INFO if settings.environment == "development" else logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):  # type: ignore
    # Startup
    logger.info("Starting up AI RPG Backend...")
    logger.info(f"Environment: {settings.environment}")
    yield
    # Shutdown
    logger.info("Shutting down AI RPG Backend...")


# Create FastAPI app with async context manager
app = FastAPI(
    title=settings.api_title,
    description=settings.api_description,
    version=settings.api_version,
    lifespan=lifespan
)

# Configure CORS
# In production, allow specific frontend URLs and Vercel preview deployments
allowed_origins = ["*"] if settings.environment == "development" else [
    settings.frontend_url,
    "https://gen-ai-rpg.vercel.app",  # Production domain
    "https://gen-ai-rpg-pablitomaestros-projects.vercel.app",  # Assigned domain 1
    "https://gen-ai-rpg-pablitomaestro-pablitomaestros-projects.vercel.app",  # Assigned domain 2
    "https://gen-ai-ncziqxthg-pablitomaestros-projects.vercel.app",  # Preview domain
    "https://frontend-kjpmxr9eu-pablitomaestros-projects.vercel.app",
    "https://frontend-gnbv22xtk-pablitomaestros-projects.vercel.app",
    "https://frontend-six-ivory-65.vercel.app",
    "https://frontend-pablitomaestros-projects.vercel.app",
    # Allow all Vercel preview deployments
    "https://*.vercel.app",
    "https://*-pablitomaestros-projects.vercel.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(characters.router, prefix="/api/characters", tags=["characters"])
app.include_router(stories.router, prefix="/api/stories", tags=["stories"])
app.include_router(images.router, prefix="/api/images", tags=["images"])

# Include test endpoints in development mode
if settings.environment == "development":
    app.include_router(test_endpoints.router, tags=["testing"])
    logger.info("Test endpoints enabled at /api/test")


@app.get("/")
async def root() -> dict[str, str]:
    return {
        "message": "AI RPG Backend API",
        "version": settings.api_version,
        "environment": settings.environment,
        "docs": "/docs"
    }
