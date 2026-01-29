from fastapi.testclient import TestClient
from main import app
import uuid

client = TestClient(app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}

def test_user_crud():
    name = f"taro-{uuid.uuid4().hex[:8]}"

    # Create
    r = client.post("/users", json={"name": name})
    assert r.status_code == 200
    created = r.json()
    assert "id" in created
    user_id = created["id"]
    assert created["name"] == name

    # Read
    r = client.get(f"/users/{user_id}")
    assert r.status_code == 200
    assert r.json()["name"] == name

    # Update
    new_name = f"jiro-{uuid.uuid4().hex[:8]}"
    r = client.put(f"/users/{user_id}", json={"name": new_name})
    assert r.status_code == 200
    assert r.json()["name"] == new_name

    # Delete
    r = client.delete(f"/users/{user_id}")
    assert r.status_code == 200
    assert r.json()["deleted"] is True
    assert r.json()["id"] == user_id

    # After delete -> 404
    r = client.get(f"/users/{user_id}")
    assert r.status_code == 404
