from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.utils.security import get_current_user, get_current_organization, require_role
from app.models.user import User
from app.models.organization import Organization
from app.schemas.store import (
    ProductCreate, ProductUpdate, ProductDetailResponse, ProductListResponse,
    ProductCategoryCreate, ProductCategoryResponse,
    ProductTierCreate, ProductTierResponse,
    ProductScreenshotCreate, ProductScreenshotResponse,
    StoreDashboardResponse,
)
from app.services.store_service import StoreService
from uuid import UUID
from typing import Optional

router = APIRouter(prefix="/store", tags=["store"])


@router.get("/dashboard", response_model=StoreDashboardResponse)
async def store_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    org: Organization = Depends(get_current_organization),
    _: None = Depends(require_role("admin", "member")),
):
    return await StoreService.get_dashboard(db, org.id)


@router.get("/products", response_model=dict)
async def list_products(
    category_id: Optional[UUID] = None,
    status: Optional[str] = None,
    featured: Optional[bool] = None,
    page: int = 1,
    per_page: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    org: Organization = Depends(get_current_organization),
    _: None = Depends(require_role("admin", "member", "viewer")),
):
    products, total = await StoreService.list_products(
        db, org.id, category_id, status, featured, page, per_page
    )
    return {"products": products, "total": total, "page": page, "per_page": per_page}


@router.get("/products/{product_id}", response_model=ProductDetailResponse)
async def get_product(
    product_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    org: Organization = Depends(get_current_organization),
    _: None = Depends(require_role("admin", "member", "viewer")),
):
    product = await StoreService.get_product(db, org.id, product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product


@router.post("/products", response_model=ProductDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    data: ProductCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    org: Organization = Depends(get_current_organization),
    _: None = Depends(require_role("admin")),
):
    product = await StoreService.create_product(db, org.id, data)
    return await StoreService.get_product(db, org.id, product.id)


@router.patch("/products/{product_id}", response_model=ProductDetailResponse)
async def update_product(
    product_id: UUID,
    data: ProductUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    org: Organization = Depends(get_current_organization),
    _: None = Depends(require_role("admin")),
):
    product = await StoreService.update_product(db, org.id, product_id, data)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return await StoreService.get_product(db, org.id, product.id)


@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    org: Organization = Depends(get_current_organization),
    _: None = Depends(require_role("admin")),
):
    deleted = await StoreService.delete_product(db, org.id, product_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")


@router.post("/products/{product_id}/screenshots", response_model=ProductScreenshotResponse, status_code=status.HTTP_201_CREATED)
async def add_screenshot(
    product_id: UUID,
    data: ProductScreenshotCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    org: Organization = Depends(get_current_organization),
    _: None = Depends(require_role("admin")),
):
    shot = await StoreService.add_screenshot(db, org.id, product_id, data)
    if not shot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return shot


@router.post("/products/{product_id}/screenshots/upload", response_model=ProductScreenshotResponse, status_code=status.HTTP_201_CREATED)
async def upload_screenshot(
    product_id: UUID,
    file: UploadFile = File(...),
    alt_text: Optional[str] = None,
    is_mockup: bool = False,
    mockup_frame: Optional[str] = None,
    sort_order: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    org: Organization = Depends(get_current_organization),
    _: None = Depends(require_role("admin")),
):
    result = await StoreService.get_product(db, org.id, product_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    import hashlib, os

    ALLOWED_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
    MAX_SIZE = 10 * 1024 * 1024

    content_type = file.content_type or ""
    if content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail=f"Invalid file type '{content_type}'. Allowed: {', '.join(sorted(ALLOWED_TYPES))}")

    contents = await file.read()
    if len(contents) > MAX_SIZE:
        raise HTTPException(status_code=400, detail=f"File too large ({len(contents)} bytes). Max: {MAX_SIZE} bytes")

    ext = os.path.splitext(file.filename or "image.png")[1].lower() or ".png"
    safe_ext = ext if ext in {".jpg", ".jpeg", ".png", ".gif", ".webp"} else ".png"
    filename = f"{product_id}/{hashlib.sha256(contents).hexdigest()[:16]}{safe_ext}"

    upload_dir = os.path.join("uploads", "screenshots")
    os.makedirs(upload_dir, exist_ok=True)
    filepath = os.path.join(upload_dir, filename)
    with open(filepath, "wb") as f:
        f.write(contents)

    url = f"/uploads/screenshots/{filename}"
    shot = await StoreService.add_screenshot(db, org.id, product_id, ProductScreenshotCreate(
        url=url,
        alt_text=alt_text,
        is_mockup=is_mockup,
        mockup_frame=mockup_frame,
        sort_order=sort_order,
    ))
    return shot


@router.delete("/screenshots/{screenshot_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_screenshot(
    screenshot_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_role("admin")),
):
    deleted = await StoreService.delete_screenshot(db, screenshot_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Screenshot not found")


@router.post("/products/{product_id}/tiers", response_model=ProductTierResponse, status_code=status.HTTP_201_CREATED)
async def add_tier(
    product_id: UUID,
    data: ProductTierCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    org: Organization = Depends(get_current_organization),
    _: None = Depends(require_role("admin")),
):
    tier = await StoreService.add_tier(db, org.id, product_id, data)
    if not tier:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return tier


@router.delete("/tiers/{tier_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tier(
    tier_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_role("admin")),
):
    deleted = await StoreService.delete_tier(db, tier_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tier not found")


@router.get("/categories", response_model=list[ProductCategoryResponse])
async def list_categories(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    org: Organization = Depends(get_current_organization),
    _: None = Depends(require_role("admin", "member", "viewer")),
):
    return await StoreService.list_categories(db, org.id)


@router.post("/categories", response_model=ProductCategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    data: ProductCategoryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    org: Organization = Depends(get_current_organization),
    _: None = Depends(require_role("admin")),
):
    return await StoreService.create_category(db, org.id, data)


@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    org: Organization = Depends(get_current_organization),
    _: None = Depends(require_role("admin")),
):
    deleted = await StoreService.delete_category(db, org.id, category_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
