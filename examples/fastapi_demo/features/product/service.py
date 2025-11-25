from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from typing import List, Optional

from .models import Product
from .schemas import ProductCreate, ProductUpdate


async def create_product(db: AsyncSession, product_data: ProductCreate) -> Product:
    """Create a new product"""
    # Check if SKU exists
    result = await db.execute(select(Product).where(Product.sku == product_data.sku))
    existing_product = result.scalar_one_or_none()
    
    if existing_product:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product with this SKU already exists"
        )
    
    db_product = Product(**product_data.model_dump())
    
    db.add(db_product)
    try:
        await db.commit()
        await db.refresh(db_product)
        return db_product
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create product"
        )


async def get_product_by_id(db: AsyncSession, product_id: int) -> Optional[Product]:
    """Get product by ID"""
    result = await db.execute(select(Product).where(Product.id == product_id))
    return result.scalar_one_or_none()


async def get_product_by_sku(db: AsyncSession, sku: str) -> Optional[Product]:
    """Get product by SKU"""
    result = await db.execute(select(Product).where(Product.sku == sku))
    return result.scalar_one_or_none()


async def get_products(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True
) -> List[Product]:
    """Get all products with pagination"""
    query = select(Product)
    
    if active_only:
        query = query.where(Product.is_active == True)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


async def update_product(
    db: AsyncSession,
    product_id: int,
    product_data: ProductUpdate
) -> Product:
    """Update product"""
    db_product = await get_product_by_id(db, product_id)
    
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    update_data = product_data.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_product, field, value)
    
    try:
        await db.commit()
        await db.refresh(db_product)
        return db_product
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update product"
        )


async def delete_product(db: AsyncSession, product_id: int) -> bool:
    """Delete product (soft delete by setting is_active to False)"""
    db_product = await get_product_by_id(db, product_id)
    
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    db_product.is_active = False
    await db.commit()
    return True


async def update_stock(db: AsyncSession, product_id: int, quantity_change: int) -> Product:
    """Update product stock quantity"""
    db_product = await get_product_by_id(db, product_id)
    
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    new_quantity = db_product.stock_quantity + quantity_change
    
    if new_quantity < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient stock"
        )
    
    db_product.stock_quantity = new_quantity
    await db.commit()
    await db.refresh(db_product)
    return db_product
