from contextlib import asynccontextmanager

from fastapi import FastAPI, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from API.ROUTES import auth_api, folders_api, notes_api, users_api
from CORE.database import Base, engine
# Estos imports registran todas las tablas en Base.metadata antes del arranque.
from MODELS.folder import Folder  # noqa: F401
from MODELS.note import Note  # noqa: F401
from MODELS.user import User  # noqa: F401
from SERVICES.errors import ServiceError


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Adecuado durante desarrollo. Cuando se agregue Alembic, las migraciones
    # deben sustituir create_all como mecanismo de evolución del esquema.
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Notes API",
    description="API para administrar usuarios, carpetas y notas.",
    version="1.0.0",
    lifespan=lifespan,
)


# Permite consumir la API desde Flutter Web durante el desarrollo. Los clientes
# móviles nativos no dependen de CORS. En producción se deben limitar los orígenes.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth_api.router)
app.include_router(users_api.router)
app.include_router(folders_api.router)
app.include_router(notes_api.router)


@app.exception_handler(ServiceError)
def service_error_handler(_, error: ServiceError):
    return JSONResponse(status_code=error.status_code, content={"detail": error.detail})


@app.get("/")
def root():
    return {
        "message": "Notes API is running",
        "version": app.version,
        "documentation": "/docs",
    }


@app.get(
    "/health/database",
    responses={status.HTTP_503_SERVICE_UNAVAILABLE: {"description": "Database unavailable"}},
)
def database_health(response: Response):
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return {"database": "connected"}
    except SQLAlchemyError:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"database": "disconnected"}
