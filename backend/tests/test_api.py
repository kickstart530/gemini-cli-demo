from datetime import datetime, timedelta


def test_health(test_client):
    resp = test_client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"


def test_register_and_login(test_client):
    resp = test_client.post("/api/auth/register", json={
        "email": "new@test.com",
        "name": "New User",
        "password": "pass123",
    })
    assert resp.status_code == 201
    assert resp.json()["email"] == "new@test.com"

    resp = test_client.post("/api/auth/login", json={
        "email": "new@test.com",
        "password": "pass123",
    })
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_register_duplicate_email(test_client):
    test_client.post("/api/auth/register", json={
        "email": "dup@test.com", "name": "User", "password": "pass",
    })
    resp = test_client.post("/api/auth/register", json={
        "email": "dup@test.com", "name": "User2", "password": "pass2",
    })
    assert resp.status_code == 400


def test_get_me(test_client, auth_headers):
    resp = test_client.get("/api/auth/me", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["email"] == "test@test.com"


def test_create_event(test_client, auth_headers):
    future = (datetime.utcnow() + timedelta(days=30)).isoformat()
    resp = test_client.post("/api/events", json={
        "title": "Test Event",
        "description": "A test event",
        "venue": "Test Venue",
        "date": future,
        "capacity": 100,
        "ticket_types": [
            {"name": "General", "price": 50.0, "quantity": 80},
            {"name": "VIP", "price": 150.0, "quantity": 20},
        ],
    }, headers=auth_headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Test Event"
    assert len(data["ticket_types"]) == 2


def test_list_events(test_client, auth_headers):
    future = (datetime.utcnow() + timedelta(days=30)).isoformat()
    test_client.post("/api/events", json={
        "title": "Event 1", "date": future, "capacity": 50,
    }, headers=auth_headers)
    resp = test_client.get("/api/events")
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


def test_get_event(test_client, auth_headers):
    future = (datetime.utcnow() + timedelta(days=30)).isoformat()
    create_resp = test_client.post("/api/events", json={
        "title": "Get Me", "date": future, "capacity": 50,
    }, headers=auth_headers)
    event_id = create_resp.json()["id"]
    resp = test_client.get(f"/api/events/{event_id}")
    assert resp.status_code == 200
    assert resp.json()["title"] == "Get Me"


def test_update_event(test_client, auth_headers):
    future = (datetime.utcnow() + timedelta(days=30)).isoformat()
    create_resp = test_client.post("/api/events", json={
        "title": "Original", "date": future, "capacity": 50,
    }, headers=auth_headers)
    event_id = create_resp.json()["id"]
    resp = test_client.put(f"/api/events/{event_id}", json={
        "title": "Updated",
    }, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["title"] == "Updated"


def test_publish_event(test_client, auth_headers):
    future = (datetime.utcnow() + timedelta(days=30)).isoformat()
    create_resp = test_client.post("/api/events", json={
        "title": "Draft Event", "date": future, "capacity": 50,
    }, headers=auth_headers)
    event_id = create_resp.json()["id"]
    assert create_resp.json()["status"] == "draft"

    resp = test_client.post(f"/api/events/{event_id}/publish", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["status"] == "published"


def test_delete_event(test_client, auth_headers):
    future = (datetime.utcnow() + timedelta(days=30)).isoformat()
    create_resp = test_client.post("/api/events", json={
        "title": "Delete Me", "date": future, "capacity": 50,
    }, headers=auth_headers)
    event_id = create_resp.json()["id"]
    resp = test_client.delete(f"/api/events/{event_id}", headers=auth_headers)
    assert resp.status_code == 204


def test_register_for_event(test_client, auth_headers):
    future = (datetime.utcnow() + timedelta(days=30)).isoformat()
    create_resp = test_client.post("/api/events", json={
        "title": "Reg Event", "date": future, "capacity": 50,
    }, headers=auth_headers)
    event_id = create_resp.json()["id"]
    resp = test_client.post(f"/api/events/{event_id}/register", headers=auth_headers)
    assert resp.status_code == 201


def test_purchase_ticket(test_client, auth_headers):
    future = (datetime.utcnow() + timedelta(days=30)).isoformat()
    create_resp = test_client.post("/api/events", json={
        "title": "Ticket Event", "date": future, "capacity": 50,
        "ticket_types": [{"name": "General", "price": 0.0, "quantity": 50}],
    }, headers=auth_headers)
    event_id = create_resp.json()["id"]
    tt_id = create_resp.json()["ticket_types"][0]["id"]
    resp = test_client.post(f"/api/events/{event_id}/tickets/purchase", json={
        "ticket_type_id": tt_id,
    }, headers=auth_headers)
    assert resp.status_code == 201
    assert resp.json()["qr_code"] is not None


def test_create_speaker(test_client, auth_headers):
    resp = test_client.post("/api/speakers", json={
        "name": "Dr. Test",
        "bio": "Test speaker bio",
    }, headers=auth_headers)
    assert resp.status_code == 201
    assert resp.json()["name"] == "Dr. Test"


def test_create_session(test_client, auth_headers):
    future = (datetime.utcnow() + timedelta(days=30)).isoformat()
    create_resp = test_client.post("/api/events", json={
        "title": "Session Event", "date": future, "capacity": 50,
    }, headers=auth_headers)
    event_id = create_resp.json()["id"]

    start = (datetime.utcnow() + timedelta(days=30)).isoformat()
    end = (datetime.utcnow() + timedelta(days=30, hours=1)).isoformat()
    resp = test_client.post(f"/api/events/{event_id}/sessions", json={
        "title": "Test Session",
        "track": "Main",
        "room": "Room 1",
        "start_time": start,
        "end_time": end,
    }, headers=auth_headers)
    assert resp.status_code == 201
    assert resp.json()["title"] == "Test Session"


def test_analytics(test_client, auth_headers):
    future = (datetime.utcnow() + timedelta(days=30)).isoformat()
    create_resp = test_client.post("/api/events", json={
        "title": "Analytics Event", "date": future, "capacity": 100,
    }, headers=auth_headers)
    event_id = create_resp.json()["id"]
    resp = test_client.get(f"/api/events/{event_id}/analytics", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["total_registrations"] == 0
