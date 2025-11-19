#!/usr/bin/env python3
"""
Migrate all avatar URLs to Firebase Storage
"""

import firebase_admin
from firebase_admin import credentials, firestore, storage
import os
import requests
from io import BytesIO
from PIL import Image
import uuid

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
            firebase_admin.initialize_app(cred, {
                'projectId': 'ai-kpi-dashboard',
                'storageBucket': 'ai-kpi-dashboard.firebasestorage.app'
            })
        except:
            firebase_admin.initialize_app(options={
                'projectId': 'ai-kpi-dashboard',
                'storageBucket': 'ai-kpi-dashboard.firebasestorage.app'
            })
    
    return firestore.client(), storage.bucket()

def upload_avatar_to_storage(bucket, url, file_path):
    """Download image from URL and upload to Firebase Storage"""
    try:
        print(f"  📥 Downloading from {url}")
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        # Process image
        image = Image.open(BytesIO(response.content))
        image = image.convert('RGB')
        image = image.resize((150, 150), Image.Resampling.LANCZOS)
        
        # Save to bytes
        img_bytes = BytesIO()
        image.save(img_bytes, format='JPEG', quality=85)
        img_bytes.seek(0)
        
        # Upload to Firebase Storage
        blob = bucket.blob(file_path)
        blob.upload_from_file(img_bytes, content_type='image/jpeg')
        blob.make_public()
        
        print(f"  ✅ Uploaded to {blob.public_url}")
        return blob.public_url
        
    except Exception as e:
        print(f"  ❌ Failed to upload: {e}")
        return None

def migrate_collection_avatars(db, bucket, collection_name, avatar_field='avatar_url'):
    """Migrate avatars for a collection"""
    print(f"\n🔄 Migrating {collection_name} avatars...")
    
    docs = db.collection(collection_name).stream()
    
    for doc in docs:
        data = doc.to_dict()
        current_url = data.get(avatar_field)
        
        if not current_url or current_url.startswith('https://storage.googleapis.com'):
            print(f"  ⏭️  Skipping {doc.id} - already migrated or no avatar")
            continue
        
        print(f"  🔄 Migrating {doc.id}...")
        
        # Upload to Firebase Storage
        file_path = f"avatars/{collection_name}/{doc.id}.jpg"
        new_url = upload_avatar_to_storage(bucket, current_url, file_path)
        
        if new_url:
            # Update document
            db.collection(collection_name).document(doc.id).update({
                avatar_field: new_url,
                'updated_at': firestore.SERVER_TIMESTAMP
            })
            print(f"  ✅ Updated {doc.id}")
        else:
            print(f"  ❌ Failed to migrate {doc.id}")

def main():
    print("🚀 Starting avatar migration to Firebase Storage...")
    
    try:
        db, bucket = init_firebase()
        print("✅ Firebase initialized")
        
        # Migrate users
        migrate_collection_avatars(db, bucket, 'users', 'avatar_url')
        
        # Migrate clients
        migrate_collection_avatars(db, bucket, 'clients', 'avatar_url')
        
        # Migrate admins
        migrate_collection_avatars(db, bucket, 'admins', 'avatar_url')
        
        print("\n🎉 Avatar migration completed!")
        print("All avatars are now stored in Firebase Storage")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")

if __name__ == "__main__":
    main()