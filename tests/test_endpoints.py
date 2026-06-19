import os
import sys

# Ensure project root is in python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_fetch_rti_queries_success():
    response = client.get("/api/v1/rti-queries")
    assert response.status_code == 200
    json_data = response.json()
    assert "data" in json_data
    assert isinstance(json_data["data"], list)
    assert json_data["error"] is None

def test_fetch_rti_queries_single_not_found():
    response = client.get("/api/v1/rti-queries?rti_query_id=not_found")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["data"] == []
    assert json_data["message"] == "No record found"

def test_fetch_rti_queries_validation_error():
    # Combining unassigned_only=True and assigned_to
    response = client.get("/api/v1/rti-queries?unassigned_only=true&assigned_to=user1")
    assert response.status_code == 400
    assert response.json()["error"] == "INVALID_FILTER_COMBINATION"

    # Invalid status ID
    response = client.get("/api/v1/rti-queries?status_id=99")
    assert response.status_code == 400
    assert response.json()["error"] == "INVALID_STATUS_ID"

def test_fetch_rti_query_count():
    response = client.get("/api/v1/rti-queries/count")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["data"]["total_count"] == 0
    assert json_data["data"]["pending_count"] == 0
    assert json_data["data"]["resolved_count"] == 0

def test_fetch_rti_query_detail_not_found():
    response = client.get("/api/v1/rti-queries/some_query_id")
    assert response.status_code == 404
    assert response.json()["error"] == "RTI_QUERY_NOT_FOUND"

def test_assign_rti_query():
    # Success mock path
    response = client.post("/api/v1/rti-queries/valid_query_id/assign")
    assert response.status_code == 200
    assert response.json()["data"]["rti_query_id"] == "valid_query_id"
    assert response.json()["data"]["assigned_to"] == "current_authenticated_user"

    # Not found mock path
    response = client.post("/api/v1/rti-queries/not_found/assign")
    assert response.status_code == 404
    assert response.json()["error"] == "RTI_QUERY_NOT_FOUND"

    # Already assigned conflict mock path
    response = client.post("/api/v1/rti-queries/already_assigned/assign")
    assert response.status_code == 409
    assert response.json()["error"] == "RTI_QUERY_ALREADY_ASSIGNED"

def test_create_inward():
    # Valid inward
    payload = {
        "department_id": 1,
        "division_id": 1,
        "sub_section_id": 1,
        "case_access_level_id": 2,
        "privacy_level_id": 3,
        "inward_priority_id": 1,
        "year": 2026
    }
    response = client.post("/api/v1/inwards", json=payload)
    assert response.status_code == 201
    assert response.json()["data"]["inward_id"] == "mock_inward_uuid"

    # Invalid access level ID
    payload["case_access_level_id"] = 99
    response = client.post("/api/v1/inwards", json=payload)
    assert response.status_code == 400
    assert response.json()["error"] == "INVALID_CASE_ACCESS_LEVEL"

    # Invalid year
    payload["case_access_level_id"] = 2
    payload["year"] = 1999
    response = client.post("/api/v1/inwards", json=payload)
    assert response.status_code == 400
    assert response.json()["error"] == "INVALID_YEAR"

def test_fetch_inward_detail_not_found():
    response = client.get("/api/v1/inwards/some_inward_id")
    assert response.status_code == 404
    assert response.json()["error"] == "INWARD_NOT_FOUND"

def test_create_office_note():
    # Valid note
    payload = {
        "inward_id": "valid_inward_id",
        "office_note": "This is an office note contents."
    }
    response = client.post("/api/v1/office-notes", json=payload)
    assert response.status_code == 201
    assert response.json()["data"]["office_note_id"] == "mock_office_note_uuid"

    # Empty note
    payload["office_note"] = ""
    response = client.post("/api/v1/office-notes", json=payload)
    assert response.status_code == 400
    assert response.json()["error"] == "EMPTY_OFFICE_NOTE"

    # Linked inward not found
    payload["office_note"] = "Valid note content"
    payload["inward_id"] = "not_found"
    response = client.post("/api/v1/office-notes", json=payload)
    assert response.status_code == 404
    assert response.json()["error"] == "INWARD_NOT_FOUND"

def test_fetch_office_note_detail_not_found():
    response = client.get("/api/v1/office-notes/some_note_id")
    assert response.status_code == 404
    assert response.json()["error"] == "OFFICE_NOTE_NOT_FOUND"

def test_submit_rti_query():
    # Valid submit
    payload = {
        "user_query": "I need info on something",
        "user_id": "user_123",
        "department_id": 5
    }
    response = client.post("/api/v1/chat/submit", json=payload)
    assert response.status_code == 201
    assert response.json()["data"]["rti_query_id"] == "mock_rti_query_uuid"
    assert response.json()["data"]["inward_id"] == "mock_inward_uuid"

    # Empty user query
    payload["user_query"] = "   "
    response = client.post("/api/v1/chat/submit", json=payload)
    assert response.status_code == 400
    assert response.json()["error"] == "EMPTY_USER_QUERY"

def test_fetch_faq():
    response = client.get("/api/v1/faqs")
    assert response.status_code == 200
    assert response.json()["data"] == []

    response = client.get("/api/v1/faqs?department=revenue")
    assert response.status_code == 200
    assert response.json()["data"] == []

def test_search_similar_queries():
    # Valid
    response = client.get("/api/v1/rti-queries/similar?rti_query=hello")
    assert response.status_code == 200
    assert response.json()["data"] == []

    # Empty query
    response = client.get("/api/v1/rti-queries/similar?rti_query=%20")
    assert response.status_code == 400
    assert response.json()["error"] == "EMPTY_RTI_QUERY"

def test_suggest_faq_match():
    # Valid
    response = client.get("/api/v1/faqs/suggest?rti_query=draft")
    assert response.status_code == 200
    assert response.json()["data"] == []

    # Empty query
    response = client.get("/api/v1/faqs/suggest?rti_query=")
    assert response.status_code == 400
    assert response.json()["error"] == "EMPTY_RTI_QUERY"

if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__]))
