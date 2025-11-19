#!/usr/bin/env python3
"""
Fix Admin Password in Firebase
Hash the admin password properly
"""

import firebase_admin
from firebase_admin import credentials, firestore
import os
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def init_firebase():
    if not firebase_admin._apps:
        try:
            service_account_info = {
                "type": "service_account",
                "project_id": "ai-kpi-dashboard",
                "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID", "dummy"),
                "private_key": os.getenv("FIREBASE_PRIVATE_KEY", "").replace('\\n', '\n'),
                "client_email": os.getenv("FIREBASE_CLIENT_EMAIL", "firebase-adminsdk@ai-kpi-dashboard.iam.gserviceaccount.com"),
                "client_id": os.getenv("FIREBASE_CLIENT_ID", "dummy"),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk%40ai-kpi-dashboard.iam.gserviceaccount.com"
            }
            
            cred = credentials.Certificate(service_account_info)
            firebase_admin.initialize_app(cred, {'projectId': 'ai-kpi-dashboard'})
        except:
            firebase_admin.initialize_app(options={'projectId': 'ai-kpi-dashboard'})
    
    return firestore.client()

def main():
    print("🔧 Fixing admin password...")
    
    try:
        db = init_firebase()
        
        # Hash the password
        hashed_password = pwd_context.hash("admin123")
        
        # Update admin document
        db.collection('admins').document('admin-1').update({
            'password_hash': hashed_password,
            'updated_at': firestore.SERVER_TIMESTAMP
        })
        
        print("✅ Admin password fixed!")
        print("You can now login with admin@oneqlek.com / admin123")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()