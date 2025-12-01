from fastapi import APIRouter, Depends, HTTPException, Query
from app.services.firebase_project_service import FirebaseProjectService
from app.schemas.common import ResponseModel
from app.utils.dependencies import get_current_admin, get_current_user
from app.models import Admin, User
from typing import List, Dict, Any

router = APIRouter()

@router.post("/", response_model=ResponseModel)
async def create_project(
    project_data: Dict[str, Any],
    current_admin: Admin = Depends(get_current_admin)
):
    """Create new project"""
    project = FirebaseProjectService.create_project(project_data)
    if not project:
        raise HTTPException(status_code=400, detail="Failed to create project")
    
    return ResponseModel(
        data=project,
        message="Project created successfully"
    )

@router.get("/", response_model=ResponseModel)
async def get_projects(
    client_id: str = Query(None),
    search: str = Query(None),
    current_admin: Admin = Depends(get_current_admin)
):
    """Get list of projects"""
    projects = FirebaseProjectService.get_projects(client_id=client_id, search=search)
    return ResponseModel(
        data=projects,
        message="Projects retrieved successfully"
    )

@router.get("/{project_id}", response_model=ResponseModel)
async def get_project(
    project_id: str,
    current_admin: Admin = Depends(get_current_admin)
):
    """Get project by ID"""
    project = FirebaseProjectService.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return ResponseModel(
        data=project,
        message="Project retrieved successfully"
    )

@router.put("/{project_id}", response_model=ResponseModel)
async def update_project(
    project_id: str,
    project_data: Dict[str, Any],
    current_admin: Admin = Depends(get_current_admin)
):
    """Update project"""
    project = FirebaseProjectService.update_project(project_id, project_data)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return ResponseModel(
        data=project,
        message="Project updated successfully"
    )

@router.delete("/{project_id}", response_model=ResponseModel)
async def delete_project(
    project_id: str,
    current_admin: Admin = Depends(get_current_admin)
):
    """Delete project"""
    success = FirebaseProjectService.delete_project(project_id)
    if not success:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return ResponseModel(message="Project deleted successfully")

@router.get("/{project_id}/dashboard-access", response_model=ResponseModel)
async def get_project_dashboard_access(
    project_id: str,
    current_admin: Admin = Depends(get_current_admin)
):
    """Get dashboard access information for a project"""
    from app.services.dashboard_deployment_service import DashboardDeploymentService
    
    access_info = await DashboardDeploymentService.get_dashboard_access_info(project_id)
    
    return ResponseModel(
        data=access_info,
        message="Dashboard access information retrieved successfully"
    )

# User endpoints
@router.get("/user/my-projects", response_model=ResponseModel)
async def get_user_projects(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get current user's assigned projects"""
    user_id = current_user.get('id')
    if not user_id:
        raise HTTPException(status_code=400, detail="User ID not found")
    
    projects = FirebaseProjectService.get_user_projects(user_id)
    return ResponseModel(
        data=projects,
        message="User projects retrieved successfully"
    )