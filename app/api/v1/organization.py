from fastapi import APIRouter, Depends, HTTPException, Query
from app.core.firebase_db import firebase_db
from app.schemas.department import DepartmentCreate, DepartmentUpdate, DepartmentResponse
from app.schemas.group import GroupCreate, GroupUpdate, GroupResponse
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse
from app.schemas.common import ResponseModel
from app.utils.dependencies import get_current_admin
from typing import Dict, Any
import uuid

router = APIRouter()

# Department endpoints
@router.post("/departments", response_model=ResponseModel)
async def create_department(
    department_data: DepartmentCreate,
    current_admin: Dict[str, Any] = Depends(get_current_admin)
):
    """Create new department"""
    # Check if name already exists
    existing = firebase_db.get_all('departments', [('name', '==', department_data.name)])
    if existing:
        raise HTTPException(status_code=400, detail="Department name already exists")
    
    department_dict = department_data.dict()
    department = firebase_db.create('departments', department_dict, f"dept-{uuid.uuid4().hex[:8]}")
    
    if not department:
        raise HTTPException(status_code=500, detail="Failed to create department")
    
    return ResponseModel(
        data=department,
        message="Department created successfully"
    )


@router.get("/departments", response_model=ResponseModel)
async def get_departments(
    current_admin: Dict[str, Any] = Depends(get_current_admin)
):
    """Get list of departments"""
    departments = firebase_db.get_all('departments')
    return ResponseModel(
        data=departments,
        message="Departments retrieved successfully"
    )


@router.put("/departments/{department_id}", response_model=ResponseModel)
async def update_department(
    department_id: str,
    department_data: DepartmentUpdate,
    current_admin: Dict[str, Any] = Depends(get_current_admin)
):
    """Update department"""
    department = firebase_db.get_by_id('departments', department_id)
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    
    update_dict = department_data.dict(exclude_unset=True)
    if update_dict.get('name'):
        # Check if new name already exists
        existing = firebase_db.get_all('departments', [('name', '==', update_dict['name'])])
        existing = [d for d in existing if d['id'] != department_id]
        if existing:
            raise HTTPException(status_code=400, detail="Department name already exists")
    
    updated_department = firebase_db.update('departments', department_id, update_dict)
    if not updated_department:
        raise HTTPException(status_code=404, detail="Department not found")
    
    return ResponseModel(
        data=updated_department,
        message="Department updated successfully"
    )


@router.delete("/departments/{department_id}", response_model=ResponseModel)
async def delete_department(
    department_id: str,
    current_admin: Dict[str, Any] = Depends(get_current_admin)
):
    """Delete department"""
    success = firebase_db.delete('departments', department_id)
    if not success:
        raise HTTPException(status_code=404, detail="Department not found")
    
    return ResponseModel(message="Department deleted successfully")


# Group endpoints
@router.post("/groups", response_model=ResponseModel)
async def create_group(
    group_data: GroupCreate,
    current_admin: Dict[str, Any] = Depends(get_current_admin)
):
    """Create new group"""
    # Check if name already exists
    existing = firebase_db.get_all('groups', [('name', '==', group_data.name)])
    if existing:
        raise HTTPException(status_code=400, detail="Group name already exists")
    
    group_dict = group_data.dict()
    group = firebase_db.create('groups', group_dict, f"g-{uuid.uuid4().hex[:8]}")
    
    if not group:
        raise HTTPException(status_code=500, detail="Failed to create group")
    
    return ResponseModel(
        data=group,
        message="Group created successfully"
    )


@router.get("/groups", response_model=ResponseModel)
async def get_groups(
    current_admin: Dict[str, Any] = Depends(get_current_admin)
):
    """Get list of groups"""
    groups = firebase_db.get_all('groups')
    return ResponseModel(
        data=groups,
        message="Groups retrieved successfully"
    )


@router.put("/groups/{group_id}", response_model=ResponseModel)
async def update_group(
    group_id: str,
    group_data: GroupUpdate,
    current_admin: Dict[str, Any] = Depends(get_current_admin)
):
    """Update group"""
    group = firebase_db.get_by_id('groups', group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    update_dict = group_data.dict(exclude_unset=True)
    if update_dict.get('name'):
        # Check if new name already exists
        existing = firebase_db.get_all('groups', [('name', '==', update_dict['name'])])
        existing = [g for g in existing if g['id'] != group_id]
        if existing:
            raise HTTPException(status_code=400, detail="Group name already exists")
    
    updated_group = firebase_db.update('groups', group_id, update_dict)
    if not updated_group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    return ResponseModel(
        data=updated_group,
        message="Group updated successfully"
    )


@router.delete("/groups/{group_id}", response_model=ResponseModel)
async def delete_group(
    group_id: str,
    current_admin: Dict[str, Any] = Depends(get_current_admin)
):
    """Delete group"""
    # Remove group from clients first
    clients = firebase_db.get_all('clients', [('group_id', '==', group_id)])
    for client in clients:
        firebase_db.update('clients', client['id'], {'group_id': None})
    
    success = firebase_db.delete('groups', group_id)
    if not success:
        raise HTTPException(status_code=404, detail="Group not found")
    
    return ResponseModel(message="Group deleted successfully")


# Category endpoints
@router.post("/categories", response_model=ResponseModel)
async def create_category(
    category_data: CategoryCreate,
    current_admin: Dict[str, Any] = Depends(get_current_admin)
):
    """Create new category"""
    # Check if name already exists
    existing = firebase_db.get_all('categories', [('name', '==', category_data.name)])
    if existing:
        raise HTTPException(status_code=400, detail="Category name already exists")
    
    category_dict = category_data.dict()
    category = firebase_db.create('categories', category_dict, f"cat-{uuid.uuid4().hex[:8]}")
    
    if not category:
        raise HTTPException(status_code=500, detail="Failed to create category")
    
    return ResponseModel(
        data=category,
        message="Category created successfully"
    )


@router.get("/categories", response_model=ResponseModel)
async def get_categories(
    current_admin: Dict[str, Any] = Depends(get_current_admin)
):
    """Get list of categories"""
    categories = firebase_db.get_all('categories')
    return ResponseModel(
        data=categories,
        message="Categories retrieved successfully"
    )


@router.put("/categories/{category_id}", response_model=ResponseModel)
async def update_category(
    category_id: str,
    category_data: CategoryUpdate,
    current_admin: Dict[str, Any] = Depends(get_current_admin)
):
    """Update category"""
    category = firebase_db.get_by_id('categories', category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    update_dict = category_data.dict(exclude_unset=True)
    if update_dict.get('name'):
        # Check if new name already exists
        existing = firebase_db.get_all('categories', [('name', '==', update_dict['name'])])
        existing = [c for c in existing if c['id'] != category_id]
        if existing:
            raise HTTPException(status_code=400, detail="Category name already exists")
    
    updated_category = firebase_db.update('categories', category_id, update_dict)
    if not updated_category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    return ResponseModel(
        data=updated_category,
        message="Category updated successfully"
    )


@router.delete("/categories/{category_id}", response_model=ResponseModel)
async def delete_category(
    category_id: str,
    current_admin: Dict[str, Any] = Depends(get_current_admin)
):
    """Delete category"""
    success = firebase_db.delete('categories', category_id)
    if not success:
        raise HTTPException(status_code=404, detail="Category not found")
    
    return ResponseModel(message="Category deleted successfully")