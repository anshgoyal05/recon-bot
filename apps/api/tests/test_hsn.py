import pytest
from app.engine.hsn import get_hsn_rate_by_date
from app.models.database import init_db
from app.services.seed import seed_database

@pytest.fixture(autouse=True)
def setup_db():
    seed_database()

def test_hsn_lookup_fasteners():
    res = get_hsn_rate_by_date("7318", "2025-02-15")
    assert res is not None
    rate, desc = res
    assert rate == 18.0
    assert "Screws" in desc or "bolts" in desc

def test_hsn_lookup_versioned_rate_change():
    # Pre-2025 auto parts HSN 8708 was 28%
    pre_2025 = get_hsn_rate_by_date("8708", "2024-06-15")
    assert pre_2025 is not None
    rate_old, _ = pre_2025
    assert rate_old == 28.0

    # 2025 onwards rationalized to 18%
    post_2025 = get_hsn_rate_by_date("8708", "2025-02-15")
    assert post_2025 is not None
    rate_new, _ = post_2025
    assert rate_new == 18.0

def test_hsn_prefix_fallback():
    # 8-digit HSN code fallback to 4-digit
    res = get_hsn_rate_by_date("73181500", "2025-02-15")
    assert res is not None
    rate, _ = res
    assert rate == 18.0
