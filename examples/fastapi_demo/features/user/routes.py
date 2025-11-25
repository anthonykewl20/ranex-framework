from fastapi import APIRouter, Depends, status
from typing import List, Any

from app.commons.database import get_db
from . import service

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: dict,
    db: Any = Depends(get_db)
):
    """Create a new user"""
    from .schemas import UserCreate
    validated_data = UserCreate(**user_data)
    user = await service.create_user(db, validated_data)
    return user


@router.get("/")
async def list_users(
    skip: int = 0,
    limit: int = 100,
    db: Any = Depends(get_db)
):
    """Get all users"""
    users = await service.get_users(db, skip=skip, limit=limit)
    return users


@router.get("/{user_id}")
async def get_user(
    user_id: int,
    db: Any = Depends(get_db)
):
    """Get user by ID"""
    user = await service.get_user_by_id(db, user_id)
    return user


@router.put("/{user_id}")
async def update_user(
    user_id: int,
    user_data: dict,
    db: Any = Depends(get_db)
):
    """Update user"""
    from .schemas import UserUpdate
    validated_data = UserUpdate(**user_data)
    user = await service.update_user(db, user_id, validated_data)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: Any = Depends(get_db)
):
    """Delete user"""
    await service.delete_user(db, user_id)
    return None
