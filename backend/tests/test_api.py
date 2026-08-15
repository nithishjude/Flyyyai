import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Set DATABASE_URL before importing app so SessionLocal picks it up
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

from app.main import app
from app.database import Base, get_db, SessionLocal
from app.models import Scan

# Use an in-memory SQLite database for testing
engine = create_engine(os.environ["DATABASE_URL"], connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

import time

def test_create_scan_invalid_path():
    response = client.post("/scans/", json={"repo_url": "/does/not/exist/anywhere"})
    assert response.status_code == 202
    scan_id = response.json()["id"]
    
    # Poll for failure
    status = "pending"
    for _ in range(10):
        res = client.get(f"/scans/{scan_id}")
        status = res.json()["status"]
        if status in ["completed", "failed"]:
            break
        time.sleep(0.5)
        
    assert status == "failed"
    assert "Repository path does not exist" in res.json()["error_message"]

def test_list_scans_empty():
    response = client.get("/scans/")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["scans"] == []

def test_create_and_delete_scan():
    # Insert a dummy scan directly to db
    db = TestingSessionLocal()
    scan = Scan(id="test-123", repo_url="test-url", status="completed")
    db.add(scan)
    db.commit()
    
    response = client.get("/scans/")
    assert response.status_code == 200
    assert response.json()["total"] == 1
    
    # Delete the scan
    delete_res = client.delete("/scans/test-123")
    assert delete_res.status_code == 204
    
    # Verify deletion
    response2 = client.get("/scans/")
    assert response2.json()["total"] == 0
