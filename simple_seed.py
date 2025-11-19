#!/usr/bin/env python3
"""
Simple Firebase Data Seeding Script
Direct Firebase seeding without complex imports
"""

import firebase_admin
from firebase_admin import credentials, firestore
import os

# Initialize Firebase
def init_firebase():
    if not firebase_admin._apps:
        # Use service account or default credentials
        try:
            # Try service account first
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
                'projectId': 'ai-kpi-dashboard'
            })
        except:
            # Fallback to default credentials
            firebase_admin.initialize_app(options={
                'projectId': 'ai-kpi-dashboard'
            })
    
    return firestore.client()

# Data to seed
CATEGORIES_DATA = [
    {'id': 'cat-1', 'name': 'E-commerce'},
    {'id': 'cat-2', 'name': 'Mobile App'},
    {'id': 'cat-3', 'name': 'SaaS Platform'},
    {'id': 'cat-4', 'name': 'Cloud Services'},
]

GROUPS_DATA = [
    {'id': 'g-1', 'name': 'Global Tech'},
    {'id': 'g-2', 'name': 'FinServ Associates'},
    {'id': 'g-3', 'name': 'Creative Collective'},
]

DEPARTMENTS_DATA = [
    {'id': 'dept-1', 'name': 'Engineering'},
    {'id': 'dept-2', 'name': 'Product'},
    {'id': 'dept-3', 'name': 'Design'},
    {'id': 'dept-4', 'name': 'Marketing & Sales'},
]

PAYMENT_PLANS_DATA = [
    {
        'id': 'plan-1', 
        'name': 'Basic', 
        'price': 299, 
        'currency': 'USD', 
        'features': ['Up to 5 projects', 'Basic support', '2 collaborators'], 
        'is_popular': False
    },
    {
        'id': 'plan-2', 
        'name': 'Pro', 
        'price': 999, 
        'currency': 'USD', 
        'features': ['Unlimited projects', 'Priority support', '10 collaborators', 'Advanced analytics'], 
        'is_popular': True
    },
    {
        'id': 'plan-3', 
        'name': 'Enterprise', 
        'price': 2999, 
        'currency': 'USD', 
        'features': ['Unlimited everything', 'Dedicated support', 'Custom integrations'], 
        'is_popular': False
    },
]

CLIENTS_DATA = [
    {
        'id': 'c-1', 
        'company': 'Innovate Inc.', 
        'email': 'john.doe@innovate.com', 
        'mobile': '555-0101', 
        'address': '123 Innovation Dr, Techville, TX', 
        'avatar_url': 'https://i.pravatar.cc/150?u=a042581f4e29026704d', 
        'group_id': 'g-1'
    },
    {
        'id': 'c-2', 
        'company': 'Solutions Co.', 
        'email': 'jane.smith@solutions.co', 
        'mobile': '555-0102', 
        'address': '456 Market St, San Francisco, CA', 
        'avatar_url': 'https://i.pravatar.cc/150?u=a042581f4e29026705d', 
        'group_id': 'g-2'
    },
    {
        'id': 'c-3', 
        'company': 'Tech Giants', 
        'email': 'peter.jones@techgiants.com', 
        'mobile': '555-0103', 
        'address': '789 Enterprise Way, New York, NY', 
        'avatar_url': 'https://i.pravatar.cc/150?u=a042581f4e29026706d', 
        'group_id': 'g-1'
    },
    {
        'id': 'c-4', 
        'company': 'Web Wizards', 
        'email': 'mary.j@webwizards.io', 
        'mobile': '555-0104', 
        'address': '101 Dev Lane, Austin, TX', 
        'avatar_url': 'https://i.pravatar.cc/150?u=a042581f4e29026707d'
    },
]

PROJECTS_DATA = [
    {
        'id': 'p-1', 
        'name': 'E-commerce Platform', 
        'client_id': 'c-1', 
        'plan_id': 'plan-2', 
        'department_id': 'dept-1', 
        'status': 'In Progress', 
        'progress': 75, 
        'start_date': '2024-05-01', 
        'dashboard_url': 'https://vercel.com/', 
        'currency': 'USD', 
        'project_type': 'Dashboard'
    },
    {
        'id': 'p-2', 
        'name': 'Mobile Banking App', 
        'client_id': 'c-2', 
        'plan_id': 'plan-3', 
        'department_id': 'dept-1', 
        'status': 'Completed', 
        'progress': 100, 
        'start_date': '2023-11-15', 
        'dashboard_url': 'https://example-dashboard.com/p2', 
        'currency': 'USD', 
        'project_type': 'Dashboard'
    },
    {
        'id': 'p-3', 
        'name': 'Marketing Campaign', 
        'client_id': 'c-3', 
        'plan_id': 'plan-1', 
        'department_id': 'dept-4', 
        'status': 'On Hold', 
        'progress': 20, 
        'start_date': '2024-06-10', 
        'currency': 'USD', 
        'project_type': 'Dashboard'
    },
    {
        'id': 'p-4', 
        'name': 'Design System', 
        'client_id': 'c-4', 
        'plan_id': 'plan-2', 
        'department_id': 'dept-3', 
        'status': 'In Progress', 
        'progress': 50, 
        'start_date': '2023-10-01', 
        'dashboard_url': 'https://example-dashboard.com/p4', 
        'currency': 'USD', 
        'project_type': 'Dashboard'
    },
    {
        'id': 'p-5', 
        'name': 'Internal Dashboard', 
        'client_id': 'c-1', 
        'plan_id': 'plan-2', 
        'department_id': 'dept-2', 
        'status': 'Completed', 
        'progress': 100, 
        'start_date': '2024-02-01', 
        'currency': 'USD', 
        'project_type': 'Dashboard'
    },
    {
        'id': 'p-6', 
        'name': 'Power BI Connector', 
        'client_id': 'c-1', 
        'plan_id': 'plan-1', 
        'department_id': 'dept-2', 
        'status': 'Completed', 
        'progress': 100, 
        'start_date': '2024-07-01', 
        'dashboard_url': 'https://powerbi.microsoft.com/', 
        'currency': 'USD', 
        'project_type': 'Add-ins', 
        'image_url': 'https://images.unsplash.com/photo-1634017839464-5c33923cb4ae?q=80&w=800&auto=format&fit=crop'
    },
]

USERS_DATA = [
    {
        'id': 'u-1', 
        'name': 'Alice Martin', 
        'email': 'alice.m@innovate.com', 
        'position': 'Project Manager', 
        'client_id': 'c-1', 
        'avatar_url': 'https://i.pravatar.cc/150?u=u1', 
        'role': 'superuser', 
        'password': 'password', 
        'dashboard_access': 'view-and-edit', 
        'project_ids': ['p-1', 'p-5', 'p-6']
    },
    {
        'id': 'u-2', 
        'name': 'Bob Johnson', 
        'email': 'bob.j@solutions.co', 
        'position': 'Lead Developer', 
        'client_id': 'c-2', 
        'avatar_url': 'https://i.pravatar.cc/150?u=u2', 
        'role': 'normal', 
        'password': 'password', 
        'dashboard_access': 'view-only', 
        'project_ids': ['p-2']
    },
    {
        'id': 'u-3', 
        'name': 'Charlie Brown', 
        'email': 'charlie.b@techgiants.com', 
        'position': 'UX Designer', 
        'client_id': 'c-3', 
        'avatar_url': 'https://i.pravatar.cc/150?u=u3', 
        'role': 'normal', 
        'password': 'password', 
        'dashboard_access': 'view-only', 
        'project_ids': ['p-3']
    },
    {
        'id': 'u-4', 
        'name': 'Diana Prince', 
        'email': 'diana.p@webwizards.io', 
        'position': 'QA Engineer', 
        'client_id': 'c-4', 
        'avatar_url': 'https://i.pravatar.cc/150?u=u4', 
        'role': 'normal', 
        'password': 'password', 
        'dashboard_access': 'view-only', 
        'project_ids': ['p-4']
    },
]

INVOICES_DATA = [
    {
        'id': 'inv-1', 
        'invoice_number': 'INV-001', 
        'client_id': 'c-1', 
        'project_id': 'p-1',
        'issue_date': '2024-06-15', 
        'due_date': '2024-07-15', 
        'items': [{'description': 'Initial Project Setup', 'quantity': 1, 'price': 12000}], 
        'status': 'Paid', 
        'type': 'manual', 
        'currency': 'USD'
    },
    {
        'id': 'inv-2', 
        'invoice_number': 'INV-002', 
        'client_id': 'c-2', 
        'project_id': 'p-2',
        'issue_date': '2024-05-30', 
        'due_date': '2024-06-30', 
        'items': [{'description': 'Phase 1 Development', 'quantity': 1, 'price': 25000}], 
        'status': 'Pending', 
        'type': 'manual', 
        'currency': 'USD'
    },
    {
        'id': 'inv-3', 
        'invoice_number': 'INV-003', 
        'client_id': 'c-3', 
        'project_id': 'p-3',
        'issue_date': '2024-05-01', 
        'due_date': '2024-06-01', 
        'items': [{'description': 'Social Media Assets', 'quantity': 1, 'price': 5000}], 
        'status': 'Overdue', 
        'type': 'manual', 
        'currency': 'USD'
    },
]

PORTFOLIO_CASES_DATA = [
    {
        'id': 'pc-1',
        'category': 'E-commerce',
        'title': 'Innovate Inc. Marketplace',
        'description': 'A complete overhaul of a legacy e-commerce platform, boosting performance by 200% and increasing user engagement through a modern UI/UX design.',
        'image_url': 'https://images.unsplash.com/photo-1522199755839-a2bacb67c546?q=80&w=800&auto=format&fit=crop',
        'link': '#'
    },
    {
        'id': 'pc-2',
        'category': 'Mobile App',
        'title': 'Solutions Co. Banking App',
        'description': 'Developed a secure and intuitive mobile banking application for iOS and Android, featuring biometric login and real-time transaction tracking.',
        'image_url': 'https://images.unsplash.com/photo-1607252650355-f7fd0460ccdb?q=80&w=800&auto=format&fit=crop',
        'link': '#'
    },
    {
        'id': 'pc-3',
        'category': 'SaaS Platform',
        'title': 'CloudFlow CRM',
        'description': 'Built a scalable CRM platform from the ground up, enabling businesses to manage customer relationships with advanced analytics and automation tools.',
        'image_url': 'https://images.unsplash.com/photo-1556740758-90de374c12ad?q=80&w=800&auto=format&fit=crop',
        'link': '#'
    }
]

ADMIN_DATA = [
    {
        'id': 'admin-1',
        'name': 'System Admin',
        'email': 'admin@oneqlek.com',
        'position': 'System Administrator',
        'password': 'admin123'
    }
]

def seed_collection(db, collection_name, data_list):
    """Seed a Firebase collection with data"""
    print(f"\n🌱 Seeding {collection_name}...")
    
    for item in data_list:
        item_id = item.pop('id')
        
        try:
            # Add timestamps
            item['created_at'] = firestore.SERVER_TIMESTAMP
            item['updated_at'] = firestore.SERVER_TIMESTAMP
            
            db.collection(collection_name).document(item_id).set(item)
            print(f"  ✅ Created {collection_name}/{item_id}")
        except Exception as e:
            print(f"  ❌ Error creating {collection_name}/{item_id}: {e}")

def clear_collection(db, collection_name):
    """Clear all documents from a Firebase collection"""
    print(f"\n🗑️  Clearing {collection_name}...")
    
    try:
        docs = db.collection(collection_name).stream()
        deleted_count = 0
        
        for doc in docs:
            doc.reference.delete()
            deleted_count += 1
            print(f"  🗑️  Deleted {collection_name}/{doc.id}")
        
        if deleted_count == 0:
            print(f"  ✅ {collection_name} is already empty")
        else:
            print(f"  ✅ Cleared {deleted_count} documents from {collection_name}")
        
    except Exception as e:
        print(f"  ❌ Error clearing {collection_name}: {e}")

def main():
    """Main function"""
    print("🚀 Starting Firebase data seeding...")
    
    try:
        db = init_firebase()
        print("✅ Firebase connection successful")
        
        # Collections to clear (in reverse dependency order)
        collections_to_clear = [
            'invoices', 'users', 'projects', 'portfolio_cases', 
            'clients', 'payment_plans', 'departments', 'groups', 
            'categories', 'admins'
        ]
        
        # Clear existing data
        for collection in collections_to_clear:
            clear_collection(db, collection)
        
        # Seed new data (in dependency order)
        seed_collection(db, 'categories', CATEGORIES_DATA.copy())
        seed_collection(db, 'groups', GROUPS_DATA.copy())
        seed_collection(db, 'departments', DEPARTMENTS_DATA.copy())
        seed_collection(db, 'payment_plans', PAYMENT_PLANS_DATA.copy())
        seed_collection(db, 'clients', CLIENTS_DATA.copy())
        seed_collection(db, 'projects', PROJECTS_DATA.copy())
        seed_collection(db, 'users', USERS_DATA.copy())
        seed_collection(db, 'invoices', INVOICES_DATA.copy())
        seed_collection(db, 'portfolio_cases', PORTFOLIO_CASES_DATA.copy())
        seed_collection(db, 'admins', ADMIN_DATA.copy())
        
        print("\n🎉 Firebase seeding completed!")
        print("\nYou can now:")
        print("1. Start your backend server")
        print("2. Login to your frontend with admin@oneqlek.com / admin123")
        print("3. All data will be loaded from Firebase")
        
    except Exception as e:
        print(f"❌ Firebase seeding failed: {e}")

if __name__ == "__main__":
    main()