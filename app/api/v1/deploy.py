from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Request, Query
from fastapi.responses import Response
from app.core.firebase_db import firebase_db
from app.schemas.common import ResponseModel
from app.utils.dependencies import get_current_admin, get_current_admin_or_user
from app.services.dashboard_deployment_service import DashboardDeploymentService
from app.services.firebase_storage_service import firebase_storage_service
from typing import Dict, Any, Optional
import mimetypes

router = APIRouter()

@router.post("/project", response_model=ResponseModel)
async def deploy_project_dashboard(
    project_id: str = Form(...),
    dashboard_file: UploadFile = File(...),
    current_admin: Dict[str, Any] = Depends(get_current_admin)
):
    """Deploy dashboard ZIP file to project"""
    
    # Validate file type
    if not dashboard_file.filename.lower().endswith('.zip'):
        raise HTTPException(status_code=400, detail="Only ZIP files are allowed")
    
    # Validate project exists
    project = firebase_db.get_by_id('projects', project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Get client info for URL generation
    client = firebase_db.get_by_id('clients', project['client_id'])
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    try:
        # Deploy dashboard
        deployment_result = await DashboardDeploymentService.deploy_project_dashboard(
            project_id=project_id,
            project_name=project['name'],
            client_name=client['company'],
            dashboard_file=dashboard_file,
            deployed_by=current_admin['id']
        )
        
        return ResponseModel(
            data=deployment_result,
            message="Dashboard deployed successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Deployment failed: {str(e)}")

@router.get("/status/{deployment_id}", response_model=ResponseModel)
async def get_deployment_status(
    deployment_id: str,
    current_admin: Dict[str, Any] = Depends(get_current_admin)
):
    """Get deployment status"""
    
    deployment = firebase_db.get_by_id('dashboard_deployments', deployment_id)
    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")
    
    return ResponseModel(
        data=deployment,
        message="Deployment status retrieved successfully"
    )

@router.delete("/project/{project_id}", response_model=ResponseModel)
async def delete_project_dashboard(
    project_id: str,
    current_admin: Dict[str, Any] = Depends(get_current_admin)
):
    """Delete project dashboard deployment"""
    
    try:
        success = await DashboardDeploymentService.delete_project_dashboard(project_id)
        if not success:
            raise HTTPException(status_code=404, detail="Dashboard deployment not found")
        
        return ResponseModel(message="Dashboard deployment deleted successfully")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete deployment: {str(e)}")

@router.get("/serve/{client_slug}/{project_slug}/{file_path:path}")
async def serve_dashboard_file(
    client_slug: str,
    project_slug: str,
    file_path: str,
    request: Request,
    token: Optional[str] = Query(None)
):
    """Serve dashboard files with authentication and access control"""
    return await serve_dashboard_file_with_auth(client_slug, project_slug, file_path, request, token)

@router.get("/assets/{file_path:path}")
async def serve_dashboard_assets(
    file_path: str,
    request: Request
):
    """Serve dashboard assets - extract client/project from referer"""
    
    # Get referer to determine which dashboard is requesting the asset
    referer = request.headers.get("referer", "")
    if not referer:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    # Extract client_slug, project_slug, and token from referer URL
    import re
    match = re.search(r'/dashboard/([^/]+)/([^/?]+)(?:\?token=([^&]+))?', referer)
    if not match:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    client_slug, project_slug, token = match.groups()
    
    # Use token from referer URL for authentication
    return await serve_dashboard_file_with_auth(client_slug, project_slug, file_path, request, token)

async def serve_dashboard_file_with_auth(
    client_slug: str,
    project_slug: str,
    file_path: str,
    request: Request,
    token: Optional[str] = Query(None)
):
    """Internal function to serve dashboard files with authentication"""
    
    # Handle authentication via query parameter for iframe requests
    current_user = None
    if token:
        try:
            from jose import JWTError, jwt
            from app.core.config import settings
            from app.core.firebase_db import firebase_db
            
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            subject: str = payload.get("sub")
            if subject and ":" in subject:
                user_id, user_type = subject.split(":", 1)
                
                if user_type == "admin":
                    user = firebase_db.get_by_id('admins', user_id)
                    if user:
                        user['user_type'] = 'admin'
                        current_user = user
                elif user_type == "user":
                    user = firebase_db.get_by_id('users', user_id)
                    if user and user.get('is_active', True):
                        user['user_type'] = 'user'
                        current_user = user
        except Exception as e:
            print(f"Token authentication failed: {e}")
    
    if not current_user:
        # Try standard bearer token authentication
        try:
            from app.utils.dependencies import get_current_admin_or_user
            from fastapi.security import HTTPAuthorizationCredentials
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token_value = auth_header.split(" ")[1]
                credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token_value)
                current_user = get_current_admin_or_user(credentials)
        except Exception:
            pass
    
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    return await serve_dashboard_file_internal(client_slug, project_slug, file_path, current_user)

async def serve_dashboard_file_internal(
    client_slug: str,
    project_slug: str,
    file_path: str,
    current_user: Dict[str, Any]
):
    """Internal function to serve dashboard files with authentication and access control"""
    
    try:
        # Validate user access to this dashboard
        access_granted = await DashboardDeploymentService.validate_dashboard_access(
            client_slug, project_slug, current_user
        )
        
        if not access_granted:
            raise HTTPException(status_code=403, detail="Access denied to this dashboard")
        
        # Construct storage path
        storage_path = f"dashboards/{client_slug}/{project_slug}/{file_path}"
        print(f"🔍 Looking for file at: {storage_path}")
        
        # Get file from Firebase Storage
        file_content = firebase_storage_service.get_file(storage_path)
        
        # If not found and file_path doesn't start with 'assets/', try adding it
        if not file_content and not file_path.startswith('assets/'):
            assets_storage_path = f"dashboards/{client_slug}/{project_slug}/assets/{file_path}"
            print(f"🔍 Trying with assets prefix: {assets_storage_path}")
            file_content = firebase_storage_service.get_file(assets_storage_path)
        
        if not file_content:
            # Try alternative project slug (check if there's a mismatch)
            from app.core.firebase_db import firebase_db
            projects = firebase_db.get_all('projects')
            clients = firebase_db.get_all('clients')
            
            # Find the actual project and client
            actual_client = None
            actual_project = None
            
            for client in clients:
                if DashboardDeploymentService._sanitize_name(client['company']) == client_slug:
                    actual_client = client
                    break
            
            if actual_client:
                for project in projects:
                    if (project['client_id'] == actual_client['id'] and 
                        project.get('dashboard_url') and 
                        f"/{client_slug}/" in project['dashboard_url']):
                        actual_project = project
                        break
            
            if actual_project:
                # Try with the actual project slug from deployment
                actual_project_slug = DashboardDeploymentService._sanitize_name(actual_project['name'])
                alt_storage_path = f"dashboards/{client_slug}/{actual_project_slug}/{file_path}"
                print(f"🔍 Trying alternative path: {alt_storage_path}")
                file_content = firebase_storage_service.get_file(alt_storage_path)
                
                # If still not found and file_path doesn't start with 'assets/', try adding it
                if not file_content and not file_path.startswith('assets/'):
                    assets_path = f"dashboards/{client_slug}/{project_slug}/assets/{file_path}"
                    print(f"🔍 Trying with assets prefix: {assets_path}")
                    file_content = firebase_storage_service.get_file(assets_path)
            
            if not file_content:
                print(f"❌ File not found at: {storage_path}")
                raise HTTPException(status_code=404, detail=f"File not found: {storage_path}")
        
        # Determine content type
        content_type, _ = mimetypes.guess_type(file_path)
        if not content_type:
            content_type = "application/octet-stream"
        
        return Response(content=file_content, media_type=content_type)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error serving file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to serve file: {str(e)}")

@router.get("/dashboard/{client_slug}/{project_slug}")
async def serve_dashboard_index(
    client_slug: str,
    project_slug: str,
    request: Request,
    token: Optional[str] = Query(None)
):
    """Serve dashboard index.html with authentication"""
    
    # Handle authentication via query parameter for iframe requests
    current_user = None
    if token:
        try:
            from jose import JWTError, jwt
            from app.core.config import settings
            from app.core.firebase_db import firebase_db
            
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            subject: str = payload.get("sub")
            if subject and ":" in subject:
                user_id, user_type = subject.split(":", 1)
                
                if user_type == "admin":
                    user = firebase_db.get_by_id('admins', user_id)
                    if user:
                        user['user_type'] = 'admin'
                        current_user = user
                elif user_type == "user":
                    user = firebase_db.get_by_id('users', user_id)
                    if user and user.get('is_active', True):
                        user['user_type'] = 'user'
                        current_user = user
        except Exception as e:
            print(f"Token authentication failed: {e}")
    
    if not current_user:
        # Try standard bearer token authentication
        try:
            from app.utils.dependencies import get_current_admin_or_user
            from fastapi.security import HTTPAuthorizationCredentials
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token_value = auth_header.split(" ")[1]
                credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token_value)
                current_user = get_current_admin_or_user(credentials)
        except Exception:
            pass
    
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    return await serve_dashboard_file_internal(client_slug, project_slug, "index.html", current_user)