import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"

def test_get_settings():
    res = client.get("/api/settings")
    assert res.status_code == 200
    data = res.json()
    assert data["company_name"] == "Precision Auto Components Pvt Ltd"
    assert data["company_gstin"] == "27AAACP1234M1ZG"

def test_get_hsn_rates():
    res = client.get("/api/hsn-rates")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 10
    hsn_codes = [r["hsn_code"] for r in data]
    assert "7318" in hsn_codes
    assert "8708" in hsn_codes

def test_get_suppliers():
    res = client.get("/api/suppliers")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 5
    names = [s["name"] for s in data]
    assert any("Tata" in n for n in names)

def test_demo_batch_upload():
    res = client.post("/api/batches/demo")
    assert res.status_code == 200
    data = res.json()
    assert "batch_id" in data
    assert data["status"] == "PROCESSING"
