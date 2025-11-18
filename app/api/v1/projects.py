from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.project_service import ProjectService
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse
from app.schemas.common import ResponseModel
from app.utils.dependencies import get_current_admin, get_current_user
from app.models import Admin, User
from typing import List

router = APIRouter()


@router.post("/", response_model=ResponseModel)
async def create_project(
    project_data: ProjectCreate,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Create new project"""
    project = ProjectService.create_project(db, project_data)
    return ResponseModel(
        data=ProjectResponse.from_orm(project).dict(),
        message="Project created successfully"
    )


@router.get("/", response_model=ResponseModel)
async def get_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    client_id: str = Query(None),
    search: str = Query(None),
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get list of projects"""
    projects = ProjectService.get_projects(
        db, skip=skip, limit=limit, client_id=client_id, search=search
    )
    return ResponseModel(
        data=[ProjectResponse.from_orm(project).dict() for project in projects],
        message="Projects retrieved successfully"
    )


@router.get("/{project_id}", response_model=ResponseModel)
async def get_project(
    project_id: str,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get project by ID"""
    project = ProjectService.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return ResponseModel(
        data=ProjectResponse.from_orm(project).dict(),
        message="Project retrieved successfully"
    )


@router.put("/{project_id}", response_model=ResponseModel)
async def update_project(
    project_id: str,
    project_data: ProjectUpdate,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Update project"""
    project = ProjectService.update_project(db, project_id, project_data)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return ResponseModel(
        data=ProjectResponse.from_orm(project).dict(),
        message="Project updated successfully"
    )


@router.delete("/{project_id}", response_model=ResponseModel)
async def delete_project(
    project_id: str,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Delete project"""
    success = ProjectService.delete_project(db, project_id)
    if not success:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return ResponseModel(message="Project deleted successfully")


# User endpoints for accessing their projects
@router.get("/user/my-projects", response_model=ResponseModel)
async def get_user_projects(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's assigned projects"""
    projects = ProjectService.get_user_projects(db, current_user.id)
    return ResponseModel(
        data=[ProjectResponse.from_orm(project).dict() for project in projects],
        message="User projects retrieved successfully"
    )