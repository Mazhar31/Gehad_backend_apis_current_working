import os
import uuid
import zipfile
import shutil
import subprocess
import tempfile
import logging
from typing import Optional, Dict, Any
from fastapi import UploadFile
from app.core.firebase_db import firebase_db
from app.services.firebase_storage_service import firebase_storage_service
import re

logger = logging.getLogger(__name__)

class DashboardDeploymentService:
    
    @staticmethod
    def _sanitize_name(name: str) -> str:
        """Convert name to URL-safe format"""
        logger.info(f"Sanitizing name: '{name}'")
        # Remove special characters except spaces and hyphens
        sanitized = re.sub(r'[^a-zA-Z0-9\s-]', '', name)
        # Replace spaces with hyphens and convert to lowercase
        sanitized = re.sub(r'\s+', '-', sanitized.strip()).lower()
        # Remove multiple consecutive hyphens
        sanitized = re.sub(r'-+', '-', sanitized)
        # Remove leading/trailing hyphens
        sanitized = sanitized.strip('-')
        logger.info(f"Sanitized result: '{sanitized}'")
        return sanitized
    
    @staticmethod
    async def deploy_project_dashboard(
        project_id: str,
        project_name: str,
        client_name: str,
        dashboard_file: UploadFile,
        deployed_by: str
    ) -> Dict[str, Any]:
        """Deploy dashboard for a specific project"""
        
        deployment_id = f"dep-{uuid.uuid4().hex[:8]}"
        
        # Create deployment record with pending status
        deployment_data = {
            'project_id': project_id,
            'deployment_type': 'project',
            'deployment_status': 'pending',
            'deployed_by': deployed_by,
            'deployed_at': firebase_db._get_current_timestamp()
        }
        
        firebase_db.create('dashboard_deployments', deployment_data, deployment_id)
        
        try:
            # Get project type to determine URL structure
            project = firebase_db.get_by_id('projects', project_id)
            project_type = project.get('project_type', 'Dashboard') if project else 'Dashboard'
            
            # Generate path and URL based on project type
            client_slug = DashboardDeploymentService._sanitize_name(client_name)
            project_slug = DashboardDeploymentService._sanitize_name(project_name)
            
            if project_type == 'Add-ins':
                storage_path = f"addins/{client_slug}/{project_slug}"
                dashboard_url = f"/addins/{client_slug}/{project_slug}"
            else:
                storage_path = f"dashboards/{client_slug}/{project_slug}"
                dashboard_url = f"/dashboard/{client_slug}/{project_slug}"
            
            # Process the ZIP file
            built_files_info = await DashboardDeploymentService._process_dashboard_zip(
                dashboard_file, storage_path
            )
            
            # Update project with dashboard URL and instance ID
            firebase_db.update('projects', project_id, {
                'dashboard_url': dashboard_url,
                'dashboard_instance_id': built_files_info['dashboard_instance_id']
            })
            
            # Update deployment record with success
            firebase_db.update('dashboard_deployments', deployment_id, {
                'deployment_status': 'success',
                'deployment_url': dashboard_url,
                'file_count': built_files_info['file_count'],
                'storage_path': storage_path,
                'dashboard_instance_id': built_files_info['dashboard_instance_id']
            })
            
            return {
                'deployment_id': deployment_id,
                'dashboard_url': dashboard_url,
                'status': 'success',
                'file_count': built_files_info['file_count'],
                'dashboard_instance_id': built_files_info['dashboard_instance_id']
            }
            
        except Exception as e:
            # Update deployment record with failure
            firebase_db.update('dashboard_deployments', deployment_id, {
                'deployment_status': 'failed',
                'error_message': str(e)
            })
            raise e
    
    @staticmethod
    async def _process_dashboard_zip(dashboard_file: UploadFile, storage_path: str) -> Dict[str, Any]:
        """Extract ZIP, build React app, and upload to Firebase Storage"""
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Save uploaded ZIP file
            zip_path = os.path.join(temp_dir, "dashboard.zip")
            with open(zip_path, "wb") as buffer:
                content = await dashboard_file.read()
                buffer.write(content)
            
            # Extract ZIP file
            extract_dir = os.path.join(temp_dir, "extracted")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            
            # Find the main project directory (should contain package.json)
            project_dir = DashboardDeploymentService._find_project_directory(extract_dir)
            if not project_dir:
                raise Exception("No package.json found in ZIP file")
            
            # Generate unique dashboard instance ID and update App.tsx
            unique_instance_id = f"dashboard-{uuid.uuid4().hex[:12]}"
            DashboardDeploymentService._update_dashboard_instance_id(project_dir, unique_instance_id)
            
            # Install dependencies and build
            build_dir = await DashboardDeploymentService._build_react_app(project_dir)
            
            # Upload built files to Firebase Storage
            file_count = await DashboardDeploymentService._upload_built_files(build_dir, storage_path)
            
            return {
                'file_count': file_count,
                'storage_path': storage_path,
                'dashboard_instance_id': unique_instance_id
            }
    
    @staticmethod
    def _find_project_directory(extract_dir: str) -> Optional[str]:
        """Find directory containing package.json"""
        for root, dirs, files in os.walk(extract_dir):
            if 'package.json' in files:
                return root
        return None
    
    @staticmethod
    async def _build_react_app(project_dir: str) -> str:
        """Install dependencies and build React app"""
        
        # Check if package.json exists
        package_json_path = os.path.join(project_dir, 'package.json')
        if not os.path.exists(package_json_path):
            raise Exception("package.json not found")
        
        try:
            # Install dependencies
            logger.info(f"Installing dependencies in {project_dir}")
            result = subprocess.run(['npm', 'install'], cwd=project_dir, check=True, capture_output=True, text=True)
            logger.info(f"npm install completed: {result.stdout}")
            
            # Build the project
            logger.info(f"Building React app in {project_dir}")
            result = subprocess.run(['npm', 'run', 'build'], cwd=project_dir, check=True, capture_output=True, text=True)
            logger.info(f"npm build completed: {result.stdout}")
            
            # Return build directory path
            build_dir = os.path.join(project_dir, 'build')
            if not os.path.exists(build_dir):
                # Try 'dist' directory as alternative
                build_dir = os.path.join(project_dir, 'dist')
                if not os.path.exists(build_dir):
                    raise Exception("Build directory not found (tried 'build' and 'dist')")
            
            return build_dir
            
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr if e.stderr else str(e)
            logger.error(f"Build process failed: {error_msg}")
            raise Exception(f"Build failed: {error_msg}")
    
    @staticmethod
    async def _upload_built_files(build_dir: str, storage_path: str) -> int:
        """Upload all built files to Firebase Storage"""
        
        file_count = 0
        
        for root, dirs, files in os.walk(build_dir):
            for file in files:
                file_path = os.path.join(root, file)
                
                # Calculate relative path from build directory
                rel_path = os.path.relpath(file_path, build_dir)
                
                # Create storage path
                storage_file_path = f"{storage_path}/{rel_path}".replace('\\', '/')
                
                # Read file content
                with open(file_path, 'rb') as f:
                    file_content = f.read()
                
                # Determine content type
                content_type = DashboardDeploymentService._get_content_type(file)
                
                # Upload to Firebase Storage
                firebase_storage_service.upload_file(
                    file_content, 
                    storage_file_path, 
                    content_type
                )
                
                file_count += 1
        
        return file_count
    
    @staticmethod
    def _update_dashboard_instance_id(project_dir: str, instance_id: str) -> None:
        """Update DASHBOARD_INSTANCE_ID in App.tsx file"""
        app_tsx_path = os.path.join(project_dir, 'App.tsx')
        
        if os.path.exists(app_tsx_path):
            try:
                # Read the file
                with open(app_tsx_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                
                # Replace the DASHBOARD_INSTANCE_ID value
                import re
                pattern = r"const DASHBOARD_INSTANCE_ID = '[^']*';"
                replacement = f"const DASHBOARD_INSTANCE_ID = '{instance_id}';"
                
                updated_content = re.sub(pattern, replacement, content)
                
                # Write back to file
                with open(app_tsx_path, 'w', encoding='utf-8') as file:
                    file.write(updated_content)
                
                logger.info(f"Updated DASHBOARD_INSTANCE_ID to {instance_id} in App.tsx")
                
            except Exception as e:
                logger.warning(f"Failed to update DASHBOARD_INSTANCE_ID in App.tsx: {e}")
        else:
            logger.warning("App.tsx not found in project directory")
    
    @staticmethod
    def _get_content_type(filename: str) -> str:
        """Get content type based on file extension"""
        ext = os.path.splitext(filename)[1].lower()
        content_types = {
            '.html': 'text/html',
            '.css': 'text/css',
            '.js': 'application/javascript',
            '.json': 'application/json',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.svg': 'image/svg+xml',
            '.ico': 'image/x-icon',
            '.woff': 'font/woff',
            '.woff2': 'font/woff2',
            '.ttf': 'font/ttf',
            '.eot': 'application/vnd.ms-fontobject'
        }
        return content_types.get(ext, 'application/octet-stream')
    
    @staticmethod
    async def validate_dashboard_access(
        client_slug: str, 
        project_slug: str, 
        current_user: Dict[str, Any]
    ) -> bool:
        """Validate if user has access to dashboard"""
        
        try:
            # Find client by slug
            clients = firebase_db.get_all('clients')
            client = None
            for c in clients:
                if DashboardDeploymentService._sanitize_name(c['company']) == client_slug:
                    client = c
                    break
            
            if not client:
                return False
            
            # Find project by slug and client
            projects = firebase_db.get_all('projects', [('client_id', '==', client['id'])])
            project = None
            for p in projects:
                if DashboardDeploymentService._sanitize_name(p['name']) == project_slug:
                    project = p
                    break
            
            if not project or not project.get('dashboard_url'):
                return False
            
            # Both Dashboard and Add-ins projects can be served through internal system
            # The project type doesn't affect access validation
            
            # Check user access
            user_type = current_user.get('user_type', 'user')
            
            if user_type == 'admin':
                # Admins have access to all dashboards
                return True
            elif user_type == 'user':
                # Regular users need to be assigned to the project and belong to the client
                user_client_id = current_user.get('client_id')
                user_project_ids = current_user.get('project_ids', [])
                
                return (user_client_id == client['id'] and project['id'] in user_project_ids)
            
            return False
            
        except Exception as e:
            print(f"Error validating dashboard access: {e}")
            return False
    
    @staticmethod
    async def delete_project_dashboard(project_id: str) -> bool:
        """Delete dashboard deployment for a project"""
        
        # Find deployment record
        deployments = firebase_db.get_all('dashboard_deployments', [
            ('project_id', '==', project_id),
            ('deployment_type', '==', 'project')
        ])
        
        if not deployments:
            return False
        
        deployment = deployments[0]  # Get the latest deployment
        
        try:
            # Delete files from Firebase Storage if storage_path exists
            if 'storage_path' in deployment:
                # Note: Firebase Storage doesn't have a direct "delete folder" API
                # This would need to be implemented based on your storage structure
                pass
            
            # Remove dashboard URL and instance ID from project
            firebase_db.update('projects', project_id, {
                'dashboard_url': None,
                'dashboard_instance_id': None
            })
            
            # Delete deployment record
            firebase_db.delete('dashboard_deployments', deployment['id'])
            
            return True
            
        except Exception as e:
            print(f"Error deleting dashboard deployment: {e}")
            return False
    
    @staticmethod
    async def handle_project_type_change(project_id: str, old_type: str, new_type: str) -> Dict[str, Any]:
        """Handle project type changes while preserving dashboard deployments"""
        
        project = firebase_db.get_by_id('projects', project_id)
        if not project:
            raise Exception("Project not found")
        
        dashboard_url = project.get('dashboard_url')
        
        # If project has a deployed dashboard
        if dashboard_url:
            # Both Dashboard and Add-ins projects work the same way
            # The deployment remains accessible regardless of project type
            return {
                'status': 'success',
                'message': f'Project type changed from {old_type} to {new_type}. Deployed files remain accessible.',
                'dashboard_url': dashboard_url,
                'access_type': 'internal' if (dashboard_url.startswith('/dashboard/') or dashboard_url.startswith('/addins/')) else 'external'
            }
        
        # No dashboard URL exists
        return {
            'status': 'success',
            'message': f'Project type changed from {old_type} to {new_type}. No dashboard deployment affected.',
            'dashboard_url': None,
            'access_type': None
        }
    
    @staticmethod
    def is_internal_dashboard_url(dashboard_url: str) -> bool:
        """Check if dashboard URL is for internal deployment or external link"""
        if not dashboard_url:
            return False
        
        # Internal URLs start with /dashboard/ or /addins/
        return dashboard_url.startswith('/dashboard/') or dashboard_url.startswith('/addins/')
    
    @staticmethod
    async def get_dashboard_access_info(project_id: str) -> Dict[str, Any]:
        """Get dashboard access information for a project"""
        
        project = firebase_db.get_by_id('projects', project_id)
        if not project:
            return {'accessible': False, 'reason': 'Project not found'}
        
        dashboard_url = project.get('dashboard_url')
        project_type = project.get('project_type', 'Dashboard')
        
        if not dashboard_url:
            return {'accessible': False, 'reason': 'No dashboard deployed'}
        
        is_internal = DashboardDeploymentService.is_internal_dashboard_url(dashboard_url)
        
        return {
            'accessible': True,
            'dashboard_url': dashboard_url,
            'project_type': project_type,
            'is_internal': is_internal,
            'access_method': 'internal' if is_internal else 'external'
        }