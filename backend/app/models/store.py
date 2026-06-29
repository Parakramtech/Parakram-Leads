import uuid
from datetime import datetime
from sqlalchemy import String, Text, Integer, Boolean, DateTime, JSON, Float, Enum as SAEnum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base
import enum


class ProductStatus(str, enum.Enum):
    LIVE = "live"
    BETA = "beta"
    BUILDING = "building"
    RND = "rnd"
    HIDDEN = "hidden"


class ProductPlatform(str, enum.Enum):
    CROSS_PLATFORM = "cross_platform"
    ANDROID = "android"
    WINDOWS = "windows"
    IOS = "ios"
    WEB = "web"
    API = "api"
    TEMPLATE = "template"


class Product(Base):
    __tablename__ = "store_products"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    tagline: Mapped[str] = mapped_column(String(255), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    category_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("store_categories.id", ondelete="SET NULL"),
        nullable=True, index=True
    )
    status: Mapped[str] = mapped_column(SAEnum(ProductStatus), default=ProductStatus.BUILDING)
    platform: Mapped[str] = mapped_column(SAEnum(ProductPlatform), default=ProductPlatform.CROSS_PLATFORM)
    price_monthly: Mapped[float | None] = mapped_column(Float, nullable=True)
    price_once: Mapped[float | None] = mapped_column(Float, nullable=True)
    external_url: Mapped[str] = mapped_column(String(512), nullable=True)
    features: Mapped[list] = mapped_column(JSON, nullable=True, default=list)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    featured: Mapped[bool] = mapped_column(Boolean, default=False)
    extra_meta: Mapped[dict] = mapped_column("metadata", JSON, nullable=True, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    soft_deleted: Mapped[bool] = mapped_column(Boolean, default=False)

    tiers: Mapped[list["ProductTier"]] = relationship(
        "ProductTier", back_populates="product",
        cascade="all, delete-orphan", lazy="selectin",
        order_by="ProductTier.sort_order",
    )
    screenshots: Mapped[list["ProductScreenshot"]] = relationship(
        "ProductScreenshot", back_populates="product",
        cascade="all, delete-orphan", lazy="selectin",
        order_by="ProductScreenshot.sort_order",
    )
    category: Mapped["ProductCategory | None"] = relationship(
        "ProductCategory", back_populates="products", lazy="selectin",
    )


class ProductTier(Base):
    __tablename__ = "store_product_tiers"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("store_products.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    interval: Mapped[str] = mapped_column(String(32), default="month")
    features: Mapped[dict] = mapped_column(JSON, nullable=True, default=dict)
    target_audience: Mapped[str] = mapped_column(String(255), nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    product: Mapped["Product"] = relationship("Product", back_populates="tiers")


class ProductScreenshot(Base):
    __tablename__ = "store_product_screenshots"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("store_products.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    url: Mapped[str] = mapped_column(String(1024), nullable=False)
    thumbnail_url: Mapped[str] = mapped_column(String(1024), nullable=True)
    alt_text: Mapped[str] = mapped_column(String(255), nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    is_mockup: Mapped[bool] = mapped_column(Boolean, default=False)
    mockup_frame: Mapped[str] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    product: Mapped["Product"] = relationship("Product", back_populates="screenshots")


class ProductCategory(Base):
    __tablename__ = "store_categories"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    slug: Mapped[str] = mapped_column(String(128), nullable=False)
    icon: Mapped[str] = mapped_column(String(64), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    products: Mapped[list["Product"]] = relationship("Product", back_populates="category")
