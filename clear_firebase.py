#!/usr/bin/env python3
"""
Firebase Data Clearing Script
Clears all collections in Firebase
"""

import sys
import os

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.core.firebase_db import firebase_db

def clear_collection(collection_name):
    """Clear all documents from a Firebase collection"""
    print(f"\n🗑️  Clearing {collection_name}...")
    
    try:
        # Get all documents
        docs = firebase_db.get_all(collection_name)
        
        if not docs:
            print(f"  ✅ {collection_name} is already empty")
            return
        
        # Delete each document
        deleted_count = 0
        for doc in docs:
            if firebase_db.delete(collection_name, doc['id']):
                deleted_count += 1
                print(f"  🗑️  Deleted {collection_name}/{doc['id']}")
            else:
                print(f"  ❌ Failed to delete {collection_name}/{doc['id']}")
        
        print(f"  ✅ Cleared {deleted_count} documents from {collection_name}")
        
    except Exception as e:
        print(f"  ❌ Error clearing {collection_name}: {e}")

def main():
    """Main clearing function"""
    print("🚀 Starting Firebase data clearing...")
    
    # Check Firebase connection
    if not firebase_db.service.db:
        print("❌ Firebase connection failed. Please check your configuration.")
        return
    
    print("✅ Firebase connection successful")
    
    # Collections to clear (in reverse dependency order)
    collections = [
        'invoices',
        'users', 
        'projects',
        'portfolio_cases',
        'clients',
        'payment_plans',
        'departments',
        'groups',
        'categories',
        'admins'
    ]
    
    # Clear all collections
    for collection in collections:
        clear_collection(collection)
    
    print("\n🎉 Firebase clearing completed!")
    print("You can now run seed_firebase.py to populate with fresh data")

if __name__ == "__main__":
    main()