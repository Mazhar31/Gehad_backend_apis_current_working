#!/usr/bin/env python3
"""
Database seeding script for OneQlek Backend
Run this script to populate the database with initial data
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.core.database import Base
from app.models import *
from app.services.admin_service import AdminService
from app.services.client_service import ClientService
from app.services.project_service import ProjectService
from app.services.user_service import UserService
from app.schemas.admin import AdminCreate
from app.schemas.client import ClientCreate
from app.schemas.user import UserCreate
from app.schemas.project import ProjectCreate
from datetime import date, datetime
from decimal import Decimal

# Create tables
Base.metadata.create_all(bind=engine)

def seed_database():
    db = SessionLocal()
    
    try:
        print("🌱 Seeding database with initial data...")
        
        # Create default admin
        print("👤 Creating default admin...")
        admin_data = AdminCreate(
            name="Admin",
            email="admin@example.com",
            password="admin123",
            position="Super Admin"
        )
        admin = AdminService.create_admin(db, admin_data)
        print(f"✅ Created admin: {admin.email}")
        
        # Create groups
        print("🏢 Creating groups...")
        groups_data = [
            {"id": "g-1", "name": "Global Tech"},
            {"id": "g-2", "name": "FinServ Associates"},
            {"id": "g-3", "name": "Creative Collective"}
        ]
        
        for group_data in groups_data:
            group = Group(**group_data)
            db.add(group)
        
        # Create departments
        print("🏛️ Creating departments...")
        departments_data = [
            {"id": "dept-1", "name": "Engineering"},
            {"id": "dept-2", "name": "Product"},
            {"id": "dept-3", "name": "Design"},
            {"id": "dept-4", "name": "Marketing & Sales"}
        ]
        
        for dept_data in departments_data:
            dept = Department(**dept_data)
            db.add(dept)
        
        # Create categories
        print("📂 Creating categories...")
        categories_data = [
            {"id": "cat-1", "name": "E-commerce"},
            {"id": "cat-2", "name": "Mobile App"},
            {"id": "cat-3", "name": "SaaS Platform"},
            {"id": "cat-4", "name": "Cloud Services"}
        ]
        
        for cat_data in categories_data:
            category = Category(**cat_data)
            db.add(category)
        
        # Create payment plans
        print("💳 Creating payment plans...")
        plans_data = [
            {
                "id": "plan-1",
                "name": "Basic",
                "price": Decimal("299.00"),
                "currency": "USD",
                "features": ["Up to 5 projects", "Basic support", "2 collaborators"],
                "is_popular": False
            },
            {
                "id": "plan-2", 
                "name": "Pro",
                "price": Decimal("999.00"),
                "currency": "USD",
                "features": ["Unlimited projects", "Priority support", "10 collaborators", "Advanced analytics"],
                "is_popular": True
            },
            {
                "id": "plan-3",
                "name": "Enterprise", 
                "price": Decimal("2999.00"),
                "currency": "USD",
                "features": ["Unlimited everything", "Dedicated support", "Custom integrations"],
                "is_popular": False
            }
        ]
        
        for plan_data in plans_data:
            plan = PaymentPlan(**plan_data)
            db.add(plan)
        
        db.commit()
        
        # Create clients
        print("🏢 Creating clients...")
        clients_data = [
            ClientCreate(
                company="Innovate Inc.",
                email="john.doe@innovate.com",
                mobile="555-0101",
                address="123 Innovation Dr, Techville, TX",
                group_id="g-1"
            ),
            ClientCreate(
                company="Solutions Co.",
                email="jane.smith@solutions.co", 
                mobile="555-0102",
                address="456 Market St, San Francisco, CA",
                group_id="g-2"
            ),
            ClientCreate(
                company="Tech Giants",
                email="peter.jones@techgiants.com",
                mobile="555-0103", 
                address="789 Enterprise Way, New York, NY",
                group_id="g-1"
            ),
            ClientCreate(
                company="Web Wizards",
                email="mary.j@webwizards.io",
                mobile="555-0104",
                address="101 Dev Lane, Austin, TX"
            )
        ]
        
        created_clients = []
        for client_data in clients_data:
            client = ClientService.create_client(db, client_data)
            created_clients.append(client)
            print(f"✅ Created client: {client.company}")
        
        # Create projects
        print("📋 Creating projects...")
        projects_data = [
            ProjectCreate(
                name="E-commerce Platform",
                client_id=created_clients[0].id,
                plan_id="plan-2",
                department_id="dept-1",
                status="In Progress",
                budget=Decimal("50000.00"),
                progress=75,
                start_date=date(2024, 5, 1),
                dashboard_url="https://vercel.com/",
                project_type="Dashboard"
            ),
            ProjectCreate(
                name="Mobile Banking App", 
                client_id=created_clients[1].id,
                plan_id="plan-3",
                department_id="dept-1",
                status="Completed",
                budget=Decimal("120000.00"),
                progress=100,
                start_date=date(2023, 11, 15),
                dashboard_url="https://example-dashboard.com/p2",
                project_type="Dashboard"
            ),
            ProjectCreate(
                name="Power BI Connector",
                client_id=created_clients[0].id,
                plan_id="plan-1", 
                department_id="dept-2",
                status="Completed",
                progress=100,
                start_date=date(2024, 7, 1),
                dashboard_url="https://powerbi.microsoft.com/",
                project_type="Add-ins"
            )
        ]
        
        created_projects = []
        for project_data in projects_data:
            project = ProjectService.create_project(db, project_data)
            created_projects.append(project)
            print(f"✅ Created project: {project.name}")
        
        # Create users
        print("👥 Creating users...")
        users_data = [
            UserCreate(
                name="Alice Martin",
                email="alice.m@innovate.com",
                password="password",
                position="Project Manager",
                client_id=created_clients[0].id,
                role="superuser",
                dashboard_access="view-and-edit",
                project_ids=[created_projects[0].id, created_projects[2].id]
            ),
            UserCreate(
                name="Bob Johnson",
                email="bob.j@solutions.co",
                password="password", 
                position="Lead Developer",
                client_id=created_clients[1].id,
                role="normal",
                dashboard_access="view-only",
                project_ids=[created_projects[1].id]
            )
        ]
        
        for user_data in users_data:
            user = UserService.create_user(db, user_data)
            print(f"✅ Created user: {user.name}")
        
        # Create portfolio cases
        print("🎨 Creating portfolio cases...")
        portfolio_data = [
            {
                "id": "pc-1",
                "category": "E-commerce",
                "title": "Innovate Inc. Marketplace",
                "description": "A complete overhaul of a legacy e-commerce platform, boosting performance by 200% and increasing user engagement through a modern UI/UX design.",
                "image_url": "https://images.unsplash.com/photo-1522199755839-a2bacb67c546?q=80&w=800&auto=format&fit=crop",
                "link": "#"
            },
            {
                "id": "pc-2", 
                "category": "Mobile App",
                "title": "Solutions Co. Banking App",
                "description": "Developed a secure and intuitive mobile banking application for iOS and Android, featuring biometric login and real-time transaction tracking.",
                "image_url": "https://images.unsplash.com/photo-1607252650355-f7fd0460ccdb?q=80&w=800&auto=format&fit=crop",
                "link": "#"
            }
        ]
        
        for case_data in portfolio_data:
            case = PortfolioCase(**case_data)
            db.add(case)
        
        db.commit()
        
        print("🎉 Database seeding completed successfully!")
        print("\n📋 Summary:")
        print(f"   • 1 Admin created (admin@example.com / admin123)")
        print(f"   • {len(created_clients)} Clients created")
        print(f"   • {len(created_projects)} Projects created") 
        print(f"   • {len(users_data)} Users created")
        print(f"   • 3 Payment plans created")
        print(f"   • 4 Departments created")
        print(f"   • 3 Groups created")
        print(f"   • 4 Categories created")
        print(f"   • 2 Portfolio cases created")
        print("\n🚀 You can now start the server and test the API!")
        
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()