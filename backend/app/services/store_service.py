from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete

from app.models.store import (
    Product, ProductTier, ProductScreenshot, ProductCategory,
    ProductStatus,
)

from app.schemas.store import (
    ProductCreate, ProductUpdate, ProductTierCreate,
    ProductScreenshotCreate, ProductCategoryCreate,
    StoreDashboardResponse, ProductListResponse, ProductDetailResponse,
)


class StoreService:

    @staticmethod
    def _to_list_response(product: Product) -> ProductListResponse:
        return ProductListResponse(
            id=product.id,
            name=product.name,
            slug=product.slug,
            tagline=product.tagline,
            status=product.status,
            platform=product.platform,
            price_monthly=product.price_monthly,
            price_once=product.price_once,
            sort_order=product.sort_order,
            featured=product.featured,
            created_at=product.created_at,
            screenshot_count=len(product.screenshots or []),
            tier_count=len(product.tiers or []),
        )

    @staticmethod
    async def get_dashboard(db: AsyncSession, org_id: UUID) -> StoreDashboardResponse:
        total = await db.scalar(
            select(func.count(Product.id)).where(
                Product.organization_id == org_id, Product.soft_deleted == False
            )
        )
        live = await db.scalar(
            select(func.count(Product.id)).where(
                Product.organization_id == org_id,
                Product.status == ProductStatus.LIVE,
                Product.soft_deleted == False,
            )
        )
        building = await db.scalar(
            select(func.count(Product.id)).where(
                Product.organization_id == org_id,
                Product.status.in_([ProductStatus.BUILDING, ProductStatus.BETA]),
                Product.soft_deleted == False,
            )
        )
        cats = await db.scalar(
            select(func.count(ProductCategory.id)).where(
                ProductCategory.organization_id == org_id
            )
        )
        screenshots = await db.scalar(
            select(func.count(ProductScreenshot.id)).where(
                ProductScreenshot.product_id.in_(
                    select(Product.id).where(
                        Product.organization_id == org_id,
                        Product.soft_deleted == False,
                    )
                )
            )
        )
        featured = await db.scalar(
            select(func.count(Product.id)).where(
                Product.organization_id == org_id,
                Product.featured == True,
                Product.soft_deleted == False,
            )
        )
        recent_result = await db.execute(
            select(Product)
            .where(Product.organization_id == org_id, Product.soft_deleted == False)
            .order_by(Product.created_at.desc())
            .limit(5)
        )
        recent = recent_result.scalars().all()

        return StoreDashboardResponse(
            total_products=total or 0,
            live_products=live or 0,
            building_products=building or 0,
            total_categories=cats or 0,
            total_screenshots=screenshots or 0,
            featured_products=featured or 0,
            recent_products=[StoreService._to_list_response(p) for p in recent],
        )

    @staticmethod
    async def list_products(
        db: AsyncSession, org_id: UUID, category_id: UUID | None = None,
        status: str | None = None, featured: bool | None = None,
        page: int = 1, per_page: int = 20,
    ) -> tuple[list[ProductListResponse], int]:
        query = select(Product).where(
            Product.organization_id == org_id, Product.soft_deleted == False
        )
        count_query = select(func.count(Product.id)).where(
            Product.organization_id == org_id, Product.soft_deleted == False
        )

        if category_id:
            query = query.where(Product.category_id == category_id)
            count_query = count_query.where(Product.category_id == category_id)
        if status:
            query = query.where(Product.status == status)
            count_query = count_query.where(Product.status == status)
        if featured is not None:
            query = query.where(Product.featured == featured)
            count_query = count_query.where(Product.featured == featured)

        total = (await db.execute(count_query)).scalar() or 0
        query = query.order_by(Product.sort_order, Product.created_at.desc())
        query = query.offset((page - 1) * per_page).limit(per_page)

        result = await db.execute(query)
        products = result.scalars().all()

        return [StoreService._to_list_response(p) for p in products], total

    @staticmethod
    async def get_product(db: AsyncSession, org_id: UUID, product_id: UUID) -> ProductDetailResponse | None:
        result = await db.execute(
            select(Product).where(
                Product.id == product_id,
                Product.organization_id == org_id,
                Product.soft_deleted == False,
            )
        )
        product = result.scalar_one_or_none()
        if not product:
            return None
        return ProductDetailResponse(
            id=product.id,
            name=product.name,
            slug=product.slug,
            tagline=product.tagline,
            description=product.description,
            status=product.status,
            platform=product.platform,
            price_monthly=product.price_monthly,
            price_once=product.price_once,
            external_url=product.external_url,
            features=product.features or [],
            sort_order=product.sort_order,
            featured=product.featured,
            metadata=product.extra_meta or {},
            created_at=product.created_at,
            updated_at=product.updated_at,
            tiers=[t for t in product.tiers] if hasattr(product, "tiers") else [],
            screenshots=[s for s in product.screenshots] if hasattr(product, "screenshots") else [],
            category=product.category,
        )

    @staticmethod
    async def create_product(
        db: AsyncSession, org_id: UUID, data: ProductCreate
    ) -> Product:
        product = Product(
            organization_id=org_id,
            name=data.name,
            slug=data.slug,
            tagline=data.tagline,
            description=data.description,
            category_id=data.category_id,
            status=data.status,
            platform=data.platform,
            price_monthly=data.price_monthly,
            price_once=data.price_once,
            external_url=data.external_url,
            features=data.features,
            sort_order=data.sort_order,
            featured=data.featured,
        )
        db.add(product)
        await db.flush()

        for t in data.tiers:
            tier = ProductTier(
                product_id=product.id,
                name=t.name,
                price=t.price,
                interval=t.interval,
                features=t.features,
                target_audience=t.target_audience,
                sort_order=t.sort_order,
                is_featured=t.is_featured,
            )
            db.add(tier)

        for s in data.screenshots:
            shot = ProductScreenshot(
                product_id=product.id,
                url=s.url,
                thumbnail_url=s.thumbnail_url,
                alt_text=s.alt_text,
                sort_order=s.sort_order,
                is_mockup=s.is_mockup,
                mockup_frame=s.mockup_frame,
            )
            db.add(shot)

        await db.commit()
        await db.refresh(product)
        return product

    @staticmethod
    async def update_product(
        db: AsyncSession, org_id: UUID, product_id: UUID, data: ProductUpdate
    ) -> Product | None:
        result = await db.execute(
            select(Product).where(
                Product.id == product_id,
                Product.organization_id == org_id,
                Product.soft_deleted == False,
            )
        )
        product = result.scalar_one_or_none()
        if not product:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(product, key, value)

        await db.commit()
        await db.refresh(product)
        return product

    @staticmethod
    async def delete_product(db: AsyncSession, org_id: UUID, product_id: UUID) -> bool:
        result = await db.execute(
            select(Product).where(
                Product.id == product_id,
                Product.organization_id == org_id,
                Product.soft_deleted == False,
            )
        )
        product = result.scalar_one_or_none()
        if not product:
            return False
        product.soft_deleted = True
        await db.commit()
        return True

    @staticmethod
    async def add_screenshot(
        db: AsyncSession, org_id: UUID, product_id: UUID, data: ProductScreenshotCreate
    ) -> ProductScreenshot | None:
        result = await db.execute(
            select(Product).where(
                Product.id == product_id,
                Product.organization_id == org_id,
                Product.soft_deleted == False,
            )
        )
        if not result.scalar_one_or_none():
            return None
        shot = ProductScreenshot(product_id=product_id, **data.model_dump())
        db.add(shot)
        await db.commit()
        await db.refresh(shot)
        return shot

    @staticmethod
    async def delete_screenshot(db: AsyncSession, screenshot_id: UUID) -> bool:
        result = await db.execute(
            select(ProductScreenshot).where(ProductScreenshot.id == screenshot_id)
        )
        shot = result.scalar_one_or_none()
        if not shot:
            return False
        await db.delete(shot)
        await db.commit()
        return True

    @staticmethod
    async def add_tier(
        db: AsyncSession, org_id: UUID, product_id: UUID, data: ProductTierCreate
    ) -> ProductTier | None:
        result = await db.execute(
            select(Product).where(
                Product.id == product_id,
                Product.organization_id == org_id,
                Product.soft_deleted == False,
            )
        )
        if not result.scalar_one_or_none():
            return None
        tier = ProductTier(product_id=product_id, **data.model_dump())
        db.add(tier)
        await db.commit()
        await db.refresh(tier)
        return tier

    @staticmethod
    async def delete_tier(db: AsyncSession, tier_id: UUID) -> bool:
        result = await db.execute(
            select(ProductTier).where(ProductTier.id == tier_id)
        )
        tier = result.scalar_one_or_none()
        if not tier:
            return False
        await db.delete(tier)
        await db.commit()
        return True

    @staticmethod
    async def list_categories(
        db: AsyncSession, org_id: UUID
    ) -> list[dict]:
        result = await db.execute(
            select(
                ProductCategory,
                func.count(Product.id).label("product_count"),
            )
            .outerjoin(
                Product,
                (Product.category_id == ProductCategory.id)
                & (Product.soft_deleted == False),
            )
            .where(ProductCategory.organization_id == org_id)
            .group_by(ProductCategory.id)
            .order_by(ProductCategory.sort_order, ProductCategory.name)
        )
        rows = result.all()
        return [
            {
                "id": cat.id,
                "name": cat.name,
                "slug": cat.slug,
                "icon": cat.icon,
                "description": cat.description,
                "sort_order": cat.sort_order,
                "product_count": count or 0,
                "created_at": cat.created_at,
            }
            for cat, count in rows
        ]

    @staticmethod
    async def create_category(
        db: AsyncSession, org_id: UUID, data: ProductCategoryCreate
    ) -> ProductCategory:
        cat = ProductCategory(organization_id=org_id, **data.model_dump())
        db.add(cat)
        await db.commit()
        await db.refresh(cat)
        return cat

    @staticmethod
    async def delete_category(db: AsyncSession, org_id: UUID, category_id: UUID) -> bool:
        result = await db.execute(
            select(ProductCategory).where(
                ProductCategory.id == category_id,
                ProductCategory.organization_id == org_id,
            )
        )
        cat = result.scalar_one_or_none()
        if not cat:
            return False
        await db.execute(
            delete(ProductCategory).where(ProductCategory.id == category_id)
        )
        await db.commit()
        return True
