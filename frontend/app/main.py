from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.config import settings
from backend.app.routers import routers

# SADECE TEK BİR APP TANIMI OLMALI
app = FastAPI(title=settings.app_name)

# SADECE TEK BİR CORS TANIMI OLMALI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for router in routers:
    app.include_router(router, prefix=settings.api_v1_prefix)