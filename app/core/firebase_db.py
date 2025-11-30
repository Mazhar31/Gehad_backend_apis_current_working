from app.services.firebase_admin_service import firebase_admin_service
from typing import Dict, List, Optional, Any
import uuid
from datetime import datetime

class FirebaseDB:
    """Firebase database operations replacing SQLAlchemy"""
    
    def __init__(self):
        self.service = firebase_admin_service

    # Generic CRUD operations
    def create(self, collection: str, data: Dict, custom_id: str = None) -> Optional[Dict]:
        """Create a new document"""
        doc_id = custom_id or f"{collection[:-1]}-{uuid.uuid4().hex[:8]}"
        
        # Add timestamps
        data.update({
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        })
        
        if self.service.create_document(collection, doc_id, data):
            return {"id": doc_id, **data}
        return None

    def get_by_id(self, collection: str, doc_id: str) -> Optional[Dict]:
        """Get document by ID"""
        return self.service.get_document(collection, doc_id)

    def get_all(self, collection: str, filters: List = None, limit: int = None) -> List[Dict]:
        """Get all documents from collection"""
        return self.service.get_collection(collection, filters, limit)

    def update(self, collection: str, doc_id: str, data: Dict) -> Optional[Dict]:
        """Update document"""
        data['updated_at'] = datetime.utcnow().isoformat()
        
        if self.service.update_document(collection, doc_id, data):
            return self.get_by_id(collection, doc_id)
        return None

    def delete(self, collection: str, doc_id: str) -> bool:
        """Delete document"""
        return self.service.delete_document(collection, doc_id)

    # Specific collection operations
    def get_projects(self, client_id: str = None, status: str = None) -> List[Dict]:
        """Get projects with optional filters"""
        filters = []
        if client_id:
            filters.append(('client_id', '==', client_id))
        if status:
            filters.append(('status', '==', status))
        return self.get_all('projects', filters)

    def get_invoices(self, client_id: str = None, status: str = None) -> List[Dict]:
        """Get invoices with optional filters"""
        filters = []
        if client_id:
            filters.append(('client_id', '==', client_id))
        if status:
            filters.append(('status', '==', status))
        return self.get_all('invoices', filters)

    def get_users_by_client(self, client_id: str) -> List[Dict]:
        """Get users by client ID"""
        return self.get_all('users', [('client_id', '==', client_id)])

    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email"""
        users = self.get_all('users', [('email', '==', email)])
        return users[0] if users else None

    def get_admin_by_email(self, email: str) -> Optional[Dict]:
        """Get admin by email"""
        admins = self.get_all('admins', [('email', '==', email)])
        return admins[0] if admins else None
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format"""
        return datetime.utcnow().isoformat()

# Global instance
firebase_db = FirebaseDB()