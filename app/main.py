from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware import Middleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.api.auth.auth import router as auth_router
from app.api.v1.admin import router as admin_router
from app.api.v1.firebase_admin import router as firebase_admin_router
from app.api.v1.firebase_clients import router as clients_router
from app.api.v1.firebase_projects import router as projects_router
from app.api.v1.firebase_users import router as users_router
from app.api.v1.firebase_invoices import router as invoices_router
from app.api.v1.user_profile import router as user_profile_router

from app.api.v1.firebase_payment_plans import router as payment_plans_router
from app.api.v1.firebase_organization import router as organization_router_firebase
from app.api.v1.firebase_portfolio import router as portfolio_router
from app.api.v1.contact import router as contact_router
from app.api.v1.upload import router as upload_router
from app.api.setup import router as setup_router
import os

# Create FastAPI app with proxy headers support
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="OneQlek Backend API - Project Management and Client Dashboard System",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    redirect_slashes=False  # Prevent automatic trailing slash redirects
)

# Add TrustedHostMiddleware first to handle proxy headers
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["*"]  # Allow all hosts for Cloud Run
)

# Add CORS middleware after TrustedHost
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for demo — allows all
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Firebase handles file storage - no local directories needed

# Include routers
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(admin_router, prefix="/api/admin", tags=["Admin"])
app.include_router(firebase_admin_router, prefix="/api/admin/firebase", tags=["Firebase Admin"])
app.include_router(clients_router, prefix="/api/admin/clients", tags=["Clients"])
app.include_router(projects_router, prefix="/api/admin/projects", tags=["Projects"])
app.include_router(users_router, prefix="/api/admin/users", tags=["Users"])
app.include_router(user_profile_router, prefix="/api/users", tags=["User Profile"])
app.include_router(invoices_router, prefix="/api/admin/invoices", tags=["Invoices"])
app.include_router(organization_router_firebase, prefix="/api/admin", tags=["Organization"])
app.include_router(payment_plans_router, prefix="/api/admin/payment-plans", tags=["Payment Plans"])
app.include_router(portfolio_router, prefix="/api/admin/portfolio", tags=["Portfolio"])
app.include_router(contact_router, prefix="/api/contact", tags=["Contact"])
app.include_router(upload_router, prefix="/api/upload", tags=["File Upload"])
app.include_router(setup_router, prefix="/api/setup", tags=["Setup"])

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
    # uvicorn.run(
    #     "app.main:app",
    #     host="0.0.0.0",
    #     port=8000,
    #     reload=settings.DEBUG
    # )
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        proxy_headers=True,
        forwarded_allow_ips="*",
        reload=settings.DEBUG
    )
