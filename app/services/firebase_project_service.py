from app.core.firebase_db import firebase_db
from typing import Optional, List, Dict
import uuid

class FirebaseProjectService:
    @staticmethod
    def create_project(project_data: Dict) -> Optional[Dict]:
        """Create a new project in Firebase"""
        project_id = f"p-{uuid.uuid4().hex[:8]}"
        
        # Get currency from payment plan
        plan = firebase_db.get_by_id('payment_plans', project_data.get('plan_id'))
        currency = plan.get('currency', 'USD') if plan else 'USD'
        
        project_doc = {
            'name': project_data.get('name'),
            'client_id': project_data.get('client_id'),
            'plan_id': project_data.get('plan_id'),
            'department_id': project_data.get('department_id'),
            'status': project_data.get('status', 'In Progress'),
            'progress': project_data.get('progress', 0),
            'start_date': project_data.get('start_date'),
            'dashboard_url': project_data.get('dashboard_url'),
            'image_url': project_data.get('image_url'),
            'project_type': project_data.get('project_type', 'Dashboard'),
            'currency': currency
        }
        
        return firebase_db.create('projects', project_doc, project_id)

    @staticmethod
    def get_project(project_id: str) -> Optional[Dict]:
        """Get project by ID"""
        return firebase_db.get_by_id('projects', project_id)

    @staticmethod
    def get_projects(client_id: str = None, search: str = None) -> List[Dict]:
        """Get all projects with optional filters"""
        filters = []
        if client_id:
            filters.append(('client_id', '==', client_id))
        
        projects = firebase_db.get_all('projects', filters)
        
        if search:
            projects = [p for p in projects if search.lower() in p.get('name', '').lower()]
        
        return projects

    @staticmethod
    def update_project(project_id: str, project_data: Dict) -> Optional[Dict]:
        """Update project"""
        return firebase_db.update('projects', project_id, project_data)

    @staticmethod
    def delete_project(project_id: str) -> bool:
        """Delete project"""
        return firebase_db.delete('projects', project_id)

    @staticmethod
    def get_user_projects(user_id: str) -> List[Dict]:
        """Get projects assigned to a user"""
        user = firebase_db.get_by_id('users', user_id)
        if not user or not user.get('project_ids'):
            return []
        
        project_ids = user.get('project_ids', [])
        projects = []
        
        for project_id in project_ids:
            project = firebase_db.get_by_id('projects', project_id)
            if project:
                projects.append(project)
        
        return projects