from fastapi import APIRouter, Depends, status, Query
from typing import Any

from app.commons.database import get_db
from . import service

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_product(
    product_data: dict,
    db: Any = Depends(get_db)
):
    """Create a new product"""
    from .models import ProductCreate
    validated_data = ProductCreate(**product_data)
    product = await service.create_product(db, validated_data)
    return product


@router.get("/")
async def list_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    active_only: bool = Query(True),
    db: Any = Depends(get_db)
):
    """Get all products"""
    products = await service.get_products(db, skip=skip, limit=limit, active_only=active_only)
    return products


@router.get("/{product_id}")
async def get_product(
    product_id: int,
    db: Any = Depends(get_db)
):
    """Get product by ID"""
    product = await service.get_product_by_id(db, product_id)
    return product


@router.get("/sku/{sku}")
async def get_product_by_sku(
    sku: str,
    db: Any = Depends(get_db)
):
    """Get product by SKU"""
    product = await service.get_product_by_sku(db, sku)
    return product


@router.put("/{product_id}")
async def update_product(
    product_id: int,
    product_data: dict,
    db: Any = Depends(get_db)
):
    """Update product"""
    from .models import ProductUpdate
    validated_data = ProductUpdate(**product_data)
    product = await service.update_product(db, product_id, validated_data)
    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: int,
    db: Any = Depends(get_db)
):
    """Delete product (soft delete)"""
    await service.delete_product(db, product_id)
    return None


@router.patch("/{product_id}/stock")
async def update_product_stock(
    product_id: int,
    quantity_change: int,
    db: Any = Depends(get_db)
):
    """Update product stock quantity"""
    product = await service.update_stock(db, product_id, quantity_change)
    return product
