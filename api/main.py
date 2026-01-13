from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from src.resources.weather_resource import router as weather_router
from prometheus_fastapi_instrumentator import Instrumentator  # ← Ajoute

tags_metadata = [
    {
        "name": "Health",
        "description": "Health check endpoints",
    },
    {
        "name": "Weather",
        "description": "Endpoints pour récupérer les données météo actuelles et les prévisions",
    },
]

app = FastAPI(
    title="CY Weather API",
    description="API for CY Weather application",
    version="0.1.0",
    openapi_tags=tags_metadata,
    redoc_url="/docs",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)

Instrumentator().instrument(app).expose(app)  # ← Ajoute cette ligne

# Si vous développez en local :
origins = [
    "http://localhost:3000",  # Si votre frontend est en React/Vue/Next
    "http://127.0.0.1:3000",
    "http://localhost:5173",  # Si vous utilisez Vite
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],           # ["*"] autorise tout, idéal pour tester
    allow_credentials=True,
    allow_methods=["*"],           # Autorise GET, POST, etc.
    allow_headers=["*"],
)

router = APIRouter(
    prefix="/api",
)

@router.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok"}

app.include_router(router)
app.include_router(weather_router, prefix="/api")
