import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1.base_query import FieldFilter
from app.core.config import settings
from typing import Dict, List, Optional, Any
import logging
import os
import json

logger = logging.getLogger(__name__)

class FirebaseAdminService:
    _instance = None
    _db = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FirebaseAdminService, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Initialize Firebase Admin SDK with service account"""
        try:
            if not firebase_admin._apps:
                # Create service account dict from environment variables
                service_account_info = {
                    "type": "service_account",
                    "project_id": settings.FIREBASE_PROJECT_ID,
                    "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID", "dummy"),
                    "private_key": os.getenv("FIREBASE_PRIVATE_KEY", "").replace('\\n', '\n'),
                    "client_email": os.getenv("FIREBASE_CLIENT_EMAIL", f"firebase-adminsdk@{settings.FIREBASE_PROJECT_ID}.iam.gserviceaccount.com"),
                    "client_id": os.getenv("FIREBASE_CLIENT_ID", "dummy"),
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                    "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk%40{settings.FIREBASE_PROJECT_ID}.iam.gserviceaccount.com"
                }
                
                # Try to initialize with service account
                try:
                    cred = credentials.Certificate(service_account_info)
                    firebase_admin.initialize_app(cred, {
                        'projectId': settings.FIREBASE_PROJECT_ID,
                        'storageBucket': settings.FIREBASE_STORAGE_BUCKET
                    })
                    logger.info(f"Firebase Admin SDK initialized with service account for project: {settings.FIREBASE_PROJECT_ID}")
                except Exception as e:
                    logger.warning(f"Service account failed: {e}")
                    # Fallback to default credentials but force project ID
                    firebase_admin.initialize_app(options={
                        'projectId': settings.FIREBASE_PROJECT_ID,
                        'storageBucket': settings.FIREBASE_STORAGE_BUCKET
                    })
                    logger.info(f"Firebase Admin SDK initialized with default credentials for project: {settings.FIREBASE_PROJECT_ID}")
                
            self._db = firestore.client()
            logger.info("Firestore client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Firebase Admin SDK: {e}")
            self._db = None

    @property
    def db(self):
        return self._db

    def create_document(self, collection: str, document_id: str, data: Dict) -> bool:
        """Create a document in Firestore"""
        try:
            if not self._db:
                logger.error("Firestore client not initialized")
                return False
                
            self._db.collection(collection).document(document_id).set(data)
            logger.info(f"Document created: {collection}/{document_id}")
            return True
        except Exception as e:
            logger.error(f"Error creating document in {collection}: {e}")
            return False

    def get_document(self, collection: str, document_id: str) -> Optional[Dict]:
        """Get a document from Firestore"""
        try:
            if not self._db:
                return None
                
            doc = self._db.collection(collection).document(document_id).get()
            if doc.exists:
                data = doc.to_dict()
                data["id"] = doc.id
                return data
            return None
        except Exception as e:
            logger.error(f"Error getting document from {collection}: {e}")
            return None

    def update_document(self, collection: str, document_id: str, data: Dict) -> bool:
        """Update a document in Firestore"""
        try:
            if not self._db:
                return False
                
            self._db.collection(collection).document(document_id).update(data)
            logger.info(f"Document updated: {collection}/{document_id}")
            return True
        except Exception as e:
            logger.error(f"Error updating document in {collection}: {e}")
            return False

    def delete_document(self, collection: str, document_id: str) -> bool:
        """Delete a document from Firestore"""
        try:
            if not self._db:
                return False
                
            self._db.collection(collection).document(document_id).delete()
            logger.info(f"Document deleted: {collection}/{document_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting document from {collection}: {e}")
            return False

    def get_collection(self, collection: str, filters: List = None, limit: int = None) -> List[Dict]:
        """Get all documents from a collection with optional filters"""
        try:
            if not self._db:
                return []
                
            query = self._db.collection(collection)
            
            if filters:
                for filter_item in filters:
                    field, operator, value = filter_item
                    query = query.where(filter=FieldFilter(field, operator, value))
            
            if limit:
                query = query.limit(limit)
            
            docs = query.stream()
            result = []
            for doc in docs:
                data = doc.to_dict()
                data["id"] = doc.id
                result.append(data)
            
            logger.info(f"Retrieved {len(result)} documents from {collection}")
            return result
        except Exception as e:
            logger.error(f"Error getting collection {collection}: {e}")
            return []

# Global instance
firebase_admin_service = FirebaseAdminService()