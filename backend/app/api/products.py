from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_, func

from app.db.database import get_db
from app.db.models import Product

router = APIRouter()

@router.get("/", status_code=status.HTTP_200_OK)
async def search_products(
    q: Optional[str] = Query(None, description="mot clé pour rechercher dans le titre ou la description"),
    category: Optional[str] = Query(None, description="filtrer par catégorie"),
    source: Optional[str] = Query(None, description="filtrer par source"),
    min_price: Optional[float] = Query(None, ge=0, description="prix minimum"),
    max_price: Optional[float] = Query(None, ge=0, description="prix maximum"),
    skip: int = Query(0, ge=0, description="nombre d'éléments à sauter pour la pagination"),
    limit: int = Query(20, ge=1, le=100, description="nombre de produits à retourner par page"),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
        recherche et filtre les produits enregistrés dans la base de données avec la pagination.
    """
    stmt = select(Product)

    # filtre par mot-cle
    if q:
        search_pattern = f"%{q}%"
        stmt = stmt.where(
            or_(
                Product.title.ilike(search_pattern),
                Product.description.ilike(search_pattern)
            )
        )

    # filtre categorie
    if category:
        stmt = stmt.where(Product.category.ilike(f"%{category}%"))

    # filtre source
    if source:
        stmt = stmt.where(Product.source.ilike(f"%{source}%"))

    # filtre prix
    if min_price is not None:
        stmt = stmt.where(Product.price >= min_price)
    if max_price is not None:
        stmt = stmt.where(Product.price <= max_price)

    # total avant pagination
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total_count = (await db.execute(count_stmt)).scalar_one()

    # pagination et tri
    stmt = stmt.order_by(Product.id.desc()).offset(skip).limit(limit)
    products = (await db.execute(stmt)).scalars().all()

    return {
        "total": total_count,
        "skip": skip,
        "limit": limit,
        "products": [
            {
                "id": p.id,
                "title": p.title,
                "price": p.price,
                "currency": p.currency,
                "category": p.category,
                "source": p.source,
                "product_url": p.product_url,
                "image_url": p.image_url,
                "created_at": p.created_at
            }
            for p in products
        ]
    }


@router.get("/compare", status_code=status.HTTP_200_OK)
async def compare_products(
    ids: List[int] = Query(..., description="liste d'identifiants de produits à comparer"),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
        compare une liste de produits sélectionnés via leurs identifiants.
    """
    if not ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="veuillez fournir au moins un identifiant de produit à comparer"
        )

    # recuperation des produits
    stmt = select(Product).where(Product.id.in_(ids))
    products = (await db.execute(stmt)).scalars().all()

    if not products:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="aucun produit trouvé pour les identifiants fournis"
        )

    # tri par prix croissant
    sorted_products = sorted(products, key=lambda p: p.price)

    prices = [p.price for p in sorted_products if p.price is not None]
    min_price = prices[0] if prices else 0.0
    max_price = prices[-1] if prices else 0.0
    price_difference = max_price - min_price

    return {
        "count": len(sorted_products),
        "metrics": {
            "min_price": min_price,
            "max_price": max_price,
            "price_difference": price_difference
        },
        "compared_products": [
            {
                "id": p.id,
                "title": p.title,
                "price": p.price,
                "currency": p.currency,
                "category": p.category,
                "source": p.source,
                "product_url": p.product_url,
                "image_url": p.image_url
            }
            for p in sorted_products
        ]
    }


@router.get("/{product_id}", status_code=status.HTTP_200_OK)
async def get_product_detail(
    product_id: int,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
        récupère les détails d'un produit spécifique via son identifiant.
    """
    stmt = select(Product).where(Product.id == product_id)
    product = (await db.execute(stmt)).scalars().first()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"produit avec l'identifiant {product_id} non trouvé"
        )

    return {
        "id": product.id,
        "title": product.title,
        "price": product.price,
        "description": product.description,
        "currency": product.currency,
        "category": product.category,
        "source": product.source,
        "product_url": product.product_url,
        "image_url": product.image_url,
        "metadata_info": product.metadata_info,
        "created_at": product.created_at
    }