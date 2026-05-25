# app/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from fastapi.openapi.utils import get_openapi
from dotenv import load_dotenv
import os

# Routers
from app.routers import auth, usuarios, roles, turnos, pacientes, kinesiologos, servicios, salas, recepcion,historias_clinicas

# Excepciones personalizadas
from app.core.exceptions import http_error_handler, generic_error_handler

# Middleware de logging
from app.core.logging_middleware import log_requests


# Cargar variables de entorno
load_dotenv()

# Inicializar app
app = FastAPI(
    title="KinesioPro API",
    description="Sistema de gestión de turnos para kinesiólogos con autenticación JWT.",
    version="2.0.0",
    openapi_tags=[
        {"name": "Autenticación", "description": "Login y registro de usuarios"},
        {"name": "Usuarios", "description": "Gestión de usuarios"},
        {"name": "Roles", "description": "Gestión de roles"},
        {"name": "Turnos", "description": "Gestión de turnos"},
        {"name": "Pacientes", "description": "Gestión de pacientes"},
        {"name": "Kinesiologos", "description": "Gestión de kinesiólogos"},
        {"name": "Salas", "description": "Gestión de salas"},
        {"name": "Servicios", "description": "Gestión de servicios"},
        {"name": "Recepción", "description": "Funcionalidades para recepcionistas"},
    ],
)

# 🔐 Seguridad global
bearer_scheme = HTTPBearer()

# ⚙️ CORS para frontend
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 📝 Middleware de logging
app.middleware("http")(log_requests)

# 🧱 Manejo global de errores
app.add_exception_handler(HTTPException, http_error_handler)
app.add_exception_handler(Exception, generic_error_handler)

# 🧾 Documentación Swagger con Bearer Token
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}
    }
    for path in openapi_schema["paths"].values():
        for method in path.values():
            method.setdefault("security", [{"BearerAuth": []}])
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# 🔌 Routers
app.include_router(auth.router)
app.include_router(usuarios.router)
app.include_router(roles.router)
app.include_router(turnos.router)
app.include_router(pacientes.router)
app.include_router(kinesiologos.router)
app.include_router(servicios.router)
app.include_router(salas.router)
app.include_router(recepcion.router)
app.include_router(historias_clinicas.router) 

@app.get("/")
def root():
    return {
        "message": "KinesioPro API v2.0",
        "docs": "/docs",
        "health": "OK"
    }
