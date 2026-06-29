import pytest
import pydantic_core
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from app.services.store_service import StoreService
from app.models.store import Product
from app.schemas.store import (
    ProductCreate, ProductUpdate, ProductScreenshotCreate, ProductCategoryCreate,
)

TEST_ORG_ID = uuid4()


def _mock_execute_result(scalar_value=None, scalars_list=None):
    """Mock for the result of await db.execute()."""
    m = MagicMock()
    if scalar_value is not None:
        m.scalar.return_value = scalar_value
    if scalars_list is not None:
        m.scalars.return_value.all.return_value = scalars_list
    if scalar_value is None and scalars_list is None:
        m.scalar_one_or_none.return_value = None
    return m


# --- Dashboard ---

@pytest.mark.asyncio
async def test_dashboard_returns_counts():
    mock_db = AsyncMock()
    mock_db.scalar = AsyncMock()
    mock_db.scalar.side_effect = [10, 3, 5, 4, 20, 2]
    mock_db.execute = AsyncMock(return_value=_mock_execute_result(scalars_list=[]))

    result = await StoreService.get_dashboard(db=mock_db, org_id=TEST_ORG_ID)

    assert result.total_products == 10
    assert result.live_products == 3
    assert result.building_products == 5
    assert result.total_categories == 4
    assert result.total_screenshots == 20
    assert result.featured_products == 2


# --- Category ---

@pytest.mark.asyncio
async def test_create_category_success():
    mock_db = AsyncMock()
    cat_id = uuid4()
    mock_db.refresh = AsyncMock(side_effect=lambda obj: setattr(obj, "id", cat_id))

    data = ProductCategoryCreate(name="Websites", slug="websites", description="Website templates")
    cat = await StoreService.create_category(db=mock_db, org_id=TEST_ORG_ID, data=data)

    assert cat.name == "Websites"
    assert cat.slug == "websites"


@pytest.mark.asyncio
async def test_list_categories_returns_list():
    mock_db = AsyncMock()
    mock_db.execute = AsyncMock(return_value=MagicMock(all=MagicMock(return_value=[])))

    cats = await StoreService.list_categories(db=mock_db, org_id=TEST_ORG_ID)

    assert isinstance(cats, list)


# --- Product ---

@pytest.mark.asyncio
async def test_create_product_with_tiers():
    mock_db = AsyncMock()
    product_id = uuid4()
    mock_db.refresh = AsyncMock(side_effect=lambda obj: setattr(obj, "id", product_id))

    data = ProductCreate(
        name="Parakram Leads",
        slug="parakram-leads",
        tagline="AI Lead Intelligence",
        description="Find and convert leads automatically.",
        status="live",
        platform="web",
        features=["Lead scraping", "AI analysis", "Multi-channel outreach"],
        tiers=[
            {
                "name": "Free",
                "price": 0,
                "interval": "month",
                "features": {"leads": "50/mo", "channels": "Email"},
                "target_audience": "Solo freelancers",
            },
            {
                "name": "Starter",
                "price": 49,
                "interval": "month",
                "features": {"leads": "500/mo", "channels": "Email + WhatsApp"},
                "target_audience": "Small agencies",
            },
        ],
    )

    product = await StoreService.create_product(db=mock_db, org_id=TEST_ORG_ID, data=data)

    assert product.id == product_id


@pytest.mark.asyncio
async def test_list_products_pagination():
    mock_db = AsyncMock()
    mock_db.execute = AsyncMock(side_effect=[
        _mock_execute_result(scalar_value=0),
        _mock_execute_result(scalars_list=[]),
    ])

    products, total = await StoreService.list_products(db=mock_db, org_id=TEST_ORG_ID, page=1, per_page=10, status="live")

    assert isinstance(products, list)
    assert total == 0


@pytest.mark.asyncio
async def test_get_product_not_found():
    mock_db = AsyncMock()
    mock_db.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=None)))

    result = await StoreService.get_product(db=mock_db, org_id=TEST_ORG_ID, product_id=uuid4())

    assert result is None


@pytest.mark.asyncio
async def test_delete_product_soft_delete():
    mock_db = AsyncMock()
    product = MagicMock(spec=Product)
    product.soft_deleted = False
    mock_db.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=product)))

    result = await StoreService.delete_product(db=mock_db, org_id=TEST_ORG_ID, product_id=uuid4())

    assert result is True
    assert product.soft_deleted is True


# --- Screenshot ---

@pytest.mark.asyncio
async def test_add_screenshot_to_product():
    mock_db = AsyncMock()
    mock_db.execute = AsyncMock(return_value=MagicMock(
        scalar_one_or_none=MagicMock(return_value=MagicMock(spec=Product))
    ))
    shot_id = uuid4()
    mock_db.refresh = AsyncMock(side_effect=lambda obj: setattr(obj, "id", shot_id))

    data = ProductScreenshotCreate(
        url="https://example.com/shot.png",
        alt_text="Dashboard screenshot",
        is_mockup=True,
        mockup_frame="iphone15",
        sort_order=1,
    )

    shot = await StoreService.add_screenshot(db=mock_db, org_id=TEST_ORG_ID, product_id=uuid4(), data=data)

    assert shot.id == shot_id


# --- Slug Validation ---

def test_create_product_validates_slug():
    with pytest.raises(pydantic_core.ValidationError):
        ProductCreate(
            name="Bad Slug",
            slug="Bad Slug With Spaces!!",
            status="live",
            platform="web",
        )


# --- Partial Update ---

@pytest.mark.asyncio
async def test_update_product_partial():
    mock_db = AsyncMock()
    product = MagicMock(spec=Product)
    product.category = None
    product.tiers = []
    product.screenshots = []
    product.features = []
    product.extra_meta = {}
    product.name = "Original Name"
    product.featured = False

    mock_db.execute = AsyncMock(return_value=MagicMock(
        scalar_one_or_none=MagicMock(return_value=product)
    ))

    data = ProductUpdate(name="Updated Name", featured=True)
    result = await StoreService.update_product(db=mock_db, org_id=TEST_ORG_ID, product_id=uuid4(), data=data)

    assert result.name == "Updated Name"
    assert result.featured is True
