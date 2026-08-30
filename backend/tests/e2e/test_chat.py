"""E2E tests - TC-001..015 golden cases."""
from fastapi.testclient import TestClient
from app.main import app
import uuid

client = TestClient(app)

def get_token():
    r = client.post("/api/v1/auth/login", data={"username":"test@orca.local","password":"test123"})
    return r.json()["access_token"]

def test_tc001_pfz_discovery():
    tok = get_token()
    r = client.post("/api/v1/chat/", json={"message":"Where is nearest PFZ today?"}, headers={"Authorization": f"Bearer {tok}"})
    assert r.status_code == 200
    assert "PFZ" in r.json()["response"] or "pfz" in r.json()["response"].lower()

def test_tc002_safety():
    tok = get_token()
    r = client.post("/api/v1/chat/", json={"message":"Is it safe to fish tomorrow near Mumbai?"}, headers={"Authorization": f"Bearer {tok}"})
    assert r.status_code == 200
    assert "risk" in r.json()["response"].lower()

def test_tc005_geofence():
    tok = get_token()
    r = client.post("/api/v1/geospatial/geofence/check?latitude=19.0&longitude=72.8", headers={"Authorization": f"Bearer {tok}"})
    assert r.status_code == 200

def test_tc008_multilingual():
    tok = get_token()
    r = client.post("/api/v1/chat/", json={"message":"मुंबई जवळ सुरक्षित आहे का?"}, headers={"Authorization": f"Bearer {tok}"})
    assert r.status_code == 200
    assert r.json()["language"] == "mr"

def test_tc009_multiturn():
    tok = get_token()
    cid = str(uuid.uuid4())
    r1 = client.post("/api/v1/chat/", json={"message":"Find fishing zones near Mumbai", "conversation_id": cid}, headers={"Authorization": f"Bearer {tok}"})
    r2 = client.post("/api/v1/chat/", json={"message":"What about tomorrow?", "conversation_id": cid}, headers={"Authorization": f"Bearer {tok}"})
    assert r1.status_code == 200 and r2.status_code == 200
    assert r1.json()["conversation_id"] == r2.json()["conversation_id"]
