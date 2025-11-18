from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.department import DepartmentCreate, DepartmentUpdate, DepartmentResponse
from app.schemas.group import GroupCreate, GroupUpdate, GroupResponse
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse
from app.schemas.common import ResponseModel
from app.utils.dependencies import get_current_admin
from app.models import Admin, Department, Group, Category
import uuid

router = APIRouter()

# Department endpoints
@router.post("/departments", response_model=ResponseModel)
async def create_department(
    department_data: DepartmentCreate,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Create new department"""
    # Check if name already exists
    existing = db.query(Department).filter(Department.name == department_data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Department name already exists")
    
    department = Department(
        id=f"dept-{uuid.uuid4().hex[:8]}",
        name=department_data.name
    )
    db.add(department)
    db.commit()
    db.refresh(department)
    
    return ResponseModel(
        data=DepartmentResponse.from_orm(department).dict(),
        message="Department created successfully"
    )


@router.get("/departments", response_model=ResponseModel)
async def get_departments(
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get list of departments"""
    departments = db.query(Department).all()
    return ResponseModel(
        data=[DepartmentResponse.from_orm(dept).dict() for dept in departments],
        message="Departments retrieved successfully"
    )


@router.put("/departments/{department_id}", response_model=ResponseModel)
async def update_department(
    department_id: str,
    department_data: DepartmentUpdate,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Update department"""
    department = db.query(Department).filter(Department.id == department_id).first()
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    
    if department_data.name:
        # Check if new name already exists
        existing = db.query(Department).filter(
            Department.name == department_data.name,
            Department.id != department_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Department name already exists")
        
        department.name = department_data.name
    
    db.commit()
    db.refresh(department)
    
    return ResponseModel(
        data=DepartmentResponse.from_orm(department).dict(),
        message="Department updated successfully"
    )


@router.delete("/departments/{department_id}", response_model=ResponseModel)
async def delete_department(
    department_id: str,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Delete department"""
    department = db.query(Department).filter(Department.id == department_id).first()
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    
    db.delete(department)
    db.commit()
    
    return ResponseModel(message="Department deleted successfully")


# Group endpoints
@router.post("/groups", response_model=ResponseModel)
async def create_group(
    group_data: GroupCreate,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Create new group"""
    # Check if name already exists
    existing = db.query(Group).filter(Group.name == group_data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Group name already exists")
    
    group = Group(
        id=f"g-{uuid.uuid4().hex[:8]}",
        name=group_data.name
    )
    db.add(group)
    db.commit()
    db.refresh(group)
    
    return ResponseModel(
        data=GroupResponse.from_orm(group).dict(),
        message="Group created successfully"
    )


@router.get("/groups", response_model=ResponseModel)
async def get_groups(
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get list of groups"""
    groups = db.query(Group).all()
    return ResponseModel(
        data=[GroupResponse.from_orm(group).dict() for group in groups],
        message="Groups retrieved successfully"
    )


@router.put("/groups/{group_id}", response_model=ResponseModel)
async def update_group(
    group_id: str,
    group_data: GroupUpdate,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Update group"""
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    if group_data.name:
        # Check if new name already exists
        existing = db.query(Group).filter(
            Group.name == group_data.name,
            Group.id != group_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Group name already exists")
        
        group.name = group_data.name
    
    db.commit()
    db.refresh(group)
    
    return ResponseModel(
        data=GroupResponse.from_orm(group).dict(),
        message="Group updated successfully"
    )


@router.delete("/groups/{group_id}", response_model=ResponseModel)
async def delete_group(
    group_id: str,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Delete group"""
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    # Remove group from clients
    from app.models import Client
    db.query(Client).filter(Client.group_id == group_id).update({"group_id": None})
    
    db.delete(group)
    db.commit()
    
    return ResponseModel(message="Group deleted successfully")


# Category endpoints
@router.post("/categories", response_model=ResponseModel)
async def create_category(
    category_data: CategoryCreate,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Create new category"""
    # Check if name already exists
    existing = db.query(Category).filter(Category.name == category_data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Category name already exists")
    
    category = Category(
        id=f"cat-{uuid.uuid4().hex[:8]}",
        name=category_data.name
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    
    return ResponseModel(
        data=CategoryResponse.from_orm(category).dict(),
        message="Category created successfully"
    )


@router.get("/categories", response_model=ResponseModel)
async def get_categories(
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get list of categories"""
    categories = db.query(Category).all()
    return ResponseModel(
        data=[CategoryResponse.from_orm(cat).dict() for cat in categories],
        message="Categories retrieved successfully"
    )


@router.put("/categories/{category_id}", response_model=ResponseModel)
async def update_category(
    category_id: str,
    category_data: CategoryUpdate,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Update category"""
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    if category_data.name:
        # Check if new name already exists
        existing = db.query(Category).filter(
            Category.name == category_data.name,
            Category.id != category_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Category name already exists")
        
        category.name = category_data.name
    
    db.commit()
    db.refresh(category)
    
    return ResponseModel(
        data=CategoryResponse.from_orm(category).dict(),
        message="Category updated successfully"
    )


@router.delete("/categories/{category_id}", response_model=ResponseModel)
async def delete_category(
    category_id: str,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Delete category"""
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    db.delete(category)
    db.commit()
    
    return ResponseModel(message="Category deleted successfully")