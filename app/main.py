from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.core.database import engine, Base
from app.api.auth.auth import router as auth_router
from app.api.v1.admin import router as admin_router
from app.api.v1.clients import router as clients_router
from app.api.v1.projects import router as projects_router
from app.api.v1.users import router as users_router
from app.api.v1.invoices import router as invoices_router
from app.api.v1.organization import router as organization_router
from app.api.v1.payment_plans import router as payment_plans_router
from app.api.v1.portfolio import router as portfolio_router
from app.api.v1.contact import router as contact_router
import os

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="OneQlek Backend API - Project Management and Client Dashboard System",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create upload directories
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(f"{settings.UPLOAD_DIR}/avatars", exist_ok=True)
os.makedirs(f"{settings.UPLOAD_DIR}/logos", exist_ok=True)
os.makedirs(f"{settings.UPLOAD_DIR}/project_images", exist_ok=True)
os.makedirs(f"{settings.UPLOAD_DIR}/portfolio_images", exist_ok=True)
os.makedirs(f"{settings.UPLOAD_DIR}/dashboards", exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory=settings.UPLOAD_DIR), name="static")

# Include routers
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(admin_router, prefix="/api/admin", tags=["Admin"])
app.include_router(clients_router, prefix="/api/admin/clients", tags=["Clients"])
app.include_router(projects_router, prefix="/api/admin/projects", tags=["Projects"])
app.include_router(users_router, prefix="/api/admin/users", tags=["Users"])
app.include_router(invoices_router, prefix="/api/admin/invoices", tags=["Invoices"])
app.include_router(organization_router, prefix="/api/admin", tags=["Organization"])
app.include_router(payment_plans_router, prefix="/api/admin/payment-plans", tags=["Payment Plans"])
app.include_router(portfolio_router, prefix="/api/admin/portfolio", tags=["Portfolio"])
app.include_router(contact_router, prefix="/api/contact", tags=["Contact"])

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal server error",
            "errors": [str(exc)] if settings.DEBUG else ["An error occurred"]
        }
    )

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "success": True,
        "message": "OneQlek Backend API is running",
        "version": "1.0.0"
    }

# Root endpoint
@app.get("/")
async def root():
    return {
        "success": True,
        "message": "Welcome to OneQlek Backend API",
        "docs": "/docs",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )