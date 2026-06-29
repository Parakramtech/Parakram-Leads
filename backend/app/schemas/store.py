from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class ProductCategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=128)
    slug: str = Field(..., min_length=1, max_length=128, pattern=r"^[a-z0-9-]+$")
    icon: Optional[str] = None
    description: Optional[str] = None
    sort_order: int = 0


class ProductCategoryResponse(BaseModel):
    id: UUID
    name: str
    slug: str
    icon: Optional[str] = None
    description: Optional[str] = None
    sort_order: int
    product_count: int = 0
    created_at: datetime

    class Config:
        from_attributes = True


class ProductTierCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=128)
    price: float = 0.0
    interval: str = "month"
    features: dict = {}
    target_audience: Optional[str] = None
    sort_order: int = 0
    is_featured: bool = False


class ProductTierResponse(BaseModel):
    id: UUID
    name: str
    price: float
    interval: str
    features: dict
    target_audience: Optional[str] = None
    sort_order: int
    is_featured: bool

    class Config:
        from_attributes = True


class ProductScreenshotCreate(BaseModel):
    url: str = Field(..., max_length=1024)
    thumbnail_url: Optional[str] = None
    alt_text: Optional[str] = None
    sort_order: int = 0
    is_mockup: bool = False
    mockup_frame: Optional[str] = None


class ProductScreenshotResponse(BaseModel):
    id: UUID
    url: str
    thumbnail_url: Optional[str] = None
    alt_text: Optional[str] = None
    sort_order: int
    is_mockup: bool
    mockup_frame: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    slug: str = Field(..., min_length=1, max_length=255, pattern=r"^[a-z0-9-]+$")
    tagline: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[UUID] = None
    status: str = "building"
    platform: str = "cross_platform"
    price_monthly: Optional[float] = None
    price_once: Optional[float] = None
    external_url: Optional[str] = None
    features: list[str] = []
    sort_order: int = 0
    featured: bool = False
    tiers: list[ProductTierCreate] = []
    screenshots: list[ProductScreenshotCreate] = []


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    tagline: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[UUID] = None
    status: Optional[str] = None
    platform: Optional[str] = None
    price_monthly: Optional[float] = None
    price_once: Optional[float] = None
    external_url: Optional[str] = None
    features: Optional[list[str]] = None
    sort_order: Optional[int] = None
    featured: Optional[bool] = None


class ProductListResponse(BaseModel):
    id: UUID
    name: str
    slug: str
    tagline: Optional[str] = None
    status: str
    platform: str
    price_monthly: Optional[float] = None
    price_once: Optional[float] = None
    category_name: Optional[str] = None
    sort_order: int
    featured: bool
    screenshot_count: int = 0
    tier_count: int = 0
    created_at: datetime

    class Config:
        from_attributes = True


class ProductDetailResponse(BaseModel):
    id: UUID
    name: str
    slug: str
    tagline: Optional[str] = None
    description: Optional[str] = None
    category: Optional[ProductCategoryResponse] = None
    status: str
    platform: str
    price_monthly: Optional[float] = None
    price_once: Optional[float] = None
    external_url: Optional[str] = None
    features: list[str]
    sort_order: int
    featured: bool
    tiers: list[ProductTierResponse] = []
    screenshots: list[ProductScreenshotResponse] = []
    metadata: dict = {}
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class StoreDashboardResponse(BaseModel):
    total_products: int
    live_products: int
    building_products: int
    total_categories: int
    total_screenshots: int
    featured_products: int
    recent_products: list[ProductListResponse] = []
