from fastapi import APIRouter, Depends, HTTPException
from app.core.firebase_db import firebase_db
from app.schemas.common import ResponseModel
from app.utils.dependencies import get_current_admin
from app.models import Admin
from typing import Dict, Any
import uuid

router = APIRouter()

# Departments
@router.post("/departments", response_model=ResponseModel)
async def create_department(
    dept_data: Dict[str, Any],
    current_admin: Admin = Depends(get_current_admin)
):
    """Create new department"""
    dept_id = f"dept-{uuid.uuid4().hex[:8]}"
    
    dept_doc = {
        'name': dept_data.get('name')
    }
    
    dept = firebase_db.create('departments', dept_doc, dept_id)
    if not dept:
        raise HTTPException(status_code=400, detail="Failed to create department")
    
    return ResponseModel(
        data=dept,
        message="Department created successfully"
    )

@router.get("/departments", response_model=ResponseModel)
async def get_departments(
    current_admin: Admin = Depends(get_current_admin)
):
    """Get all departments"""
    departments = firebase_db.get_all('departments')
    return ResponseModel(
        data=departments,
        message="Departments retrieved successfully"
    )

@router.put("/departments/{dept_id}", response_model=ResponseModel)
async def update_department(
    dept_id: str,
    dept_data: Dict[str, Any],
    current_admin: Admin = Depends(get_current_admin)
):
    """Update department"""
    dept = firebase_db.update('departments', dept_id, {'name': dept_data.get('name')})
    if not dept:
        raise HTTPException(status_code=404, detail="Department not found")
    
    return ResponseModel(
        data=dept,
        message="Department updated successfully"
    )

@router.delete("/departments/{dept_id}", response_model=ResponseModel)
async def delete_department(
    dept_id: str,
    current_admin: Admin = Depends(get_current_admin)
):
    """Delete department"""
    success = firebase_db.delete('departments', dept_id)
    if not success:
        raise HTTPException(status_code=404, detail="Department not found")
    
    return ResponseModel(message="Department deleted successfully")

# Groups
@router.post("/groups", response_model=ResponseModel)
async def create_group(
    group_data: Dict[str, Any],
    current_admin: Admin = Depends(get_current_admin)
):
    """Create new group"""
    group_id = f"g-{uuid.uuid4().hex[:8]}"
    
    group_doc = {
        'name': group_data.get('name')
    }
    
    group = firebase_db.create('groups', group_doc, group_id)
    if not group:
        raise HTTPException(status_code=400, detail="Failed to create group")
    
    return ResponseModel(
        data=group,
        message="Group created successfully"
    )

@router.get("/groups", response_model=ResponseModel)
async def get_groups(
    current_admin: Admin = Depends(get_current_admin)
):
    """Get all groups"""
    groups = firebase_db.get_all('groups')
    return ResponseModel(
        data=groups,
        message="Groups retrieved successfully"
    )

@router.put("/groups/{group_id}", response_model=ResponseModel)
async def update_group(
    group_id: str,
    group_data: Dict[str, Any],
    current_admin: Admin = Depends(get_current_admin)
):
    """Update group"""
    group = firebase_db.update('groups', group_id, {'name': group_data.get('name')})
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    return ResponseModel(
        data=group,
        message="Group updated successfully"
    )

@router.delete("/groups/{group_id}", response_model=ResponseModel)
async def delete_group(
    group_id: str,
    current_admin: Admin = Depends(get_current_admin)
):
    """Delete group"""
    success = firebase_db.delete('groups', group_id)
    if not success:
        raise HTTPException(status_code=404, detail="Group not found")
    
    return ResponseModel(message="Group deleted successfully")

# Categories
@router.post("/categories", response_model=ResponseModel)
async def create_category(
    cat_data: Dict[str, Any],
    current_admin: Admin = Depends(get_current_admin)
):
    """Create new category"""
    cat_id = f"cat-{uuid.uuid4().hex[:8]}"
    
    cat_doc = {
        'name': cat_data.get('name')
    }
    
    category = firebase_db.create('categories', cat_doc, cat_id)
    if not category:
        raise HTTPException(status_code=400, detail="Failed to create category")
    
    return ResponseModel(
        data=category,
        message="Category created successfully"
    )

@router.get("/categories", response_model=ResponseModel)
async def get_categories(
    current_admin: Admin = Depends(get_current_admin)
):
    """Get all categories"""
    categories = firebase_db.get_all('categories')
    return ResponseModel(
        data=categories,
        message="Categories retrieved successfully"
    )

@router.put("/categories/{cat_id}", response_model=ResponseModel)
async def update_category(
    cat_id: str,
    cat_data: Dict[str, Any],
    current_admin: Admin = Depends(get_current_admin)
):
    """Update category"""
    category = firebase_db.update('categories', cat_id, {'name': cat_data.get('name')})
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    return ResponseModel(
        data=category,
        message="Category updated successfully"
    )

@router.delete("/categories/{cat_id}", response_model=ResponseModel)
async def delete_category(
    cat_id: str,
    current_admin: Admin = Depends(get_current_admin)
):
    """Delete category"""
    success = firebase_db.delete('categories', cat_id)
    if not success:
        raise HTTPException(status_code=404, detail="Category not found")
    
    return ResponseModel(message="Category deleted successfully")