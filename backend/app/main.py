#backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.mongodb import db
from app.api.v1.api import router as api_router  # TODO not defined yet
from app.api.v1.endpoints.auth import router as auth_router


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,  # allow requests from these origins to api host
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Events and resource management
@app.on_event("startup")
async def startup_event():
    await db.connect_to_database()


@app.on_event("shutdown")
async def shutdown_event():
    await db.close_database_connection()


# Routes and endpoint organization
app.include_router(api_router, prefix=settings.API_V1_STR)
app.include_router(
    auth_router, prefix=f"{settings.API_V1_STR}/auth", tags=["authentication"]
)
