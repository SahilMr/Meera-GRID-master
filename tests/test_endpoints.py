import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Ensure project root is in python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.db.database import Base, get_db
from src.db.models import (
    StatusLookup, RtiQuery, SupportingDocument, OfficeNote,
    UserQuery, UserQuerySource, AssistantSuggestion, SuggestionSource,
    DepartmentMappingMaster
)
from src.main import app
from fastapi.testclient import TestClient

from sqlalchemy.pool import StaticPool
# Create in-memory test database
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)

# Seed test database with initial values
db = TestingSessionLocal()
try:
    # 1. Seed StatusLookup
    default_statuses = [
        StatusLookup(status_id=1, status_label="Pending"),
        StatusLookup(status_id=2, status_label="In Progress"),
        StatusLookup(status_id=3, status_label="Resolved"),
        StatusLookup(status_id=4, status_label="Not In Scope")
    ]
    db.add_all(default_statuses)
    db.commit()

    # 2. Seed RtiQueries
    mock_queries = [
        RtiQuery(
            rti_query_id="query_123",
            inward_id="mock_inward_uuid_1",
            query_text="This is detailed mock query text.",
            department_id=1,
            status_id=1,  # Pending
            assigned_to=None,
            assigned_at=None
        ),
        RtiQuery(
            rti_query_id="query_2",
            inward_id="mock_inward_uuid_2",
            query_text="Second mock query content",
            department_id=2,
            status_id=3,  # Resolved
            assigned_to="officer_1",
            assigned_at="2026-06-20T10:00:00Z"
        )
    ]
    db.add_all(mock_queries)
    db.commit()

    # 3. Seed Supporting Documents
    docs = [
        SupportingDocument(rti_query_id="query_123", document_url="doc_1_url"),
        SupportingDocument(rti_query_id="query_123", document_url="doc_2_url")
    ]
    db.add_all(docs)
    db.commit()

    # 4. Seed Office Notes
    notes = [
        OfficeNote(
            office_note_id="note_1",
            rti_query_id="query_123",
            office_note="Initial review of the query.",
            created_at="2026-06-20T10:00:00Z",
            created_by="officer"
        ),
        OfficeNote(
            office_note_id="note_2",
            rti_query_id="query_123",
            office_note="Updated discussion on the query.",
            created_at="2026-06-20T12:00:00Z",
            created_by="admin"
        )
    ]
    db.add_all(notes)
    db.commit()
finally:
    db.close()

# Override get_db dependency
def override_get_db():
    try:
        db_session = TestingSessionLocal()
        yield db_session
    finally:
        db_session.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

# ----------------- QUERY ENDPOINTS TESTS -----------------

def test_fetch_rti_queries_success():
    response = client.get("/api/v1/rti-queries")
    assert response.status_code == 200
    json_data = response.json()
    assert "data" in json_data
    assert isinstance(json_data["data"], list)
    assert len(json_data["data"]) == 2
    assert json_data["error"] is None

def test_fetch_rti_queries_single_success():
    response = client.get("/api/v1/rti-queries?rti_query_id=query_123")
    assert response.status_code == 200
    json_data = response.json()
    assert "data" in json_data
    assert isinstance(json_data["data"], list)
    assert len(json_data["data"]) == 1
    assert json_data["data"][0]["rti_query_id"] == "query_123"
    assert json_data["error"] is None

def test_fetch_rti_queries_single_not_found():
    response = client.get("/api/v1/rti-queries?rti_query_id=not_found")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["data"] == []
    assert json_data["message"] == "No record found"
    assert json_data["error"] is None

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
    assert json_data["data"]["total_count"] == 2
    assert json_data["data"]["pending_count"] == 1
    assert json_data["data"]["resolved_count"] == 1
    assert json_data["data"]["not_in_scope_count"] == 0
    assert json_data["data"]["active_sessions_count"] == 5

def test_fetch_rti_query_detail_success():
    response = client.get("/api/v1/rti-queries/query_123")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["data"]["rti_query_id"] == "query_123"
    assert len(json_data["data"]["office_notes"]) == 2
    # Check chronological order (Newest first)
    assert json_data["data"]["office_notes"][0]["office_note_id"] == "note_2"
    assert json_data["data"]["office_notes"][1]["office_note_id"] == "note_1"

def test_fetch_rti_query_detail_not_found():
    response = client.get("/api/v1/rti-queries/not_found")
    assert response.status_code == 404
    assert response.json()["error"] == "RTI_QUERY_NOT_FOUND"

# ----------------- CHAT ENDPOINTS TESTS -----------------

def test_user_query_success():
    payload = {
        "user_query": "Please explain the revision procedure.",
        "user_id": "user_abc",
        "rti_query_id": "query_123"
    }
    response = client.post("/api/v1/user_query", json=payload)
    assert response.status_code == 200
    json_data = response.json()
    assert isinstance(json_data["data"], list)
    assert len(json_data["data"]) == 1
    assert json_data["data"][0]["query_id"] is not None
    assert json_data["error"] is None

def test_user_query_validation_error():
    # Empty query text
    payload = {
        "user_query": "   ",
        "user_id": "user_abc",
        "rti_query_id": "query_123"
    }
    response = client.post("/api/v1/user_query", json=payload)
    assert response.status_code == 400
    assert response.json()["error"] == "EMPTY_USER_QUERY"

    # Empty user id
    payload = {
        "user_query": "Procedure?",
        "user_id": "",
        "rti_query_id": "query_123"
    }
    response = client.post("/api/v1/user_query", json=payload)
    assert response.status_code == 400
    assert response.json()["error"] == "EMPTY_USER_ID"

def test_get_suggestion_success():
    payload = {
        "rti_query_id": "query_123",
        "user_id": "user_abc"
    }
    response = client.post("/api/v1/get-suggestion", json=payload)
    assert response.status_code == 200
    json_data = response.json()
    assert isinstance(json_data["data"], list)
    assert len(json_data["data"]) == 1
    assert json_data["data"][0]["suggestion_id"] == "mock_suggestion_uuid"
    assert json_data["error"] is None

def test_get_suggestion_validation_error():
    payload = {
        "rti_query_id": "",
        "user_id": "user_abc"
    }
    response = client.post("/api/v1/get-suggestion", json=payload)
    assert response.status_code == 400
    assert response.json()["error"] == "EMPTY_RTI_QUERY_ID"

def test_get_session_success():
    response = client.get("/api/v1/get-session?rti_query_id=query_123&user_id=user_abc")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["data"]["rti_query_id"] == "query_123"
    assert len(json_data["data"]["chat"]) >= 1
    assert json_data["error"] is None

def test_get_session_not_found():
    response = client.get("/api/v1/get-session?rti_query_id=not_found&user_id=user_abc")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["data"] is None
    assert json_data["error"] is None

def test_get_session_validation_error():
    response = client.get("/api/v1/get-session?rti_query_id=&user_id=user_abc")
    assert response.status_code == 400
    assert response.json()["error"] == "EMPTY_RTI_QUERY_ID"

def test_get_session_unexpected_failure():
    response = client.get("/api/v1/get-session?rti_query_id=trigger_failure&user_id=user_abc")
    assert response.status_code == 500
    json_data = response.json()
    assert json_data["data"] == []
    assert "Simulated DB failure" in json_data["error"]

# ----------------- MASTER ENDPOINTS TESTS -----------------

def test_upload_department_master_success():
    payload = {
        "records": [
            {
                "office": "Revenue Head Office",
                "division_section": "Taxes Section",
                "sub_section": "Direct Taxes",
                "user": "officer_revenue_1"
            }
        ],
        "department": "revenue"
    }
    response = client.post("/api/v1/upload/department-mapping-master", json=payload)
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["data"][0]["upload_status"] == "success"
    assert json_data["data"][0]["total_records_uploaded"] == "1"
    assert json_data["error"] is None

def test_upload_department_master_validation_error():
    # Empty department
    payload = {
        "records": [
            {
                "office": "Revenue Head Office",
                "division_section": "Taxes Section",
                "sub_section": "Direct Taxes",
                "user": "officer_revenue_1"
            }
        ],
        "department": "   "
    }
    response = client.post("/api/v1/upload/department-mapping-master", json=payload)
    assert response.status_code == 400
    assert response.json()["error"] == "EMPTY_DEPARTMENT"

    # Empty records
    payload["department"] = "revenue"
    payload["records"] = []
    response = client.post("/api/v1/upload/department-mapping-master", json=payload)
    assert response.status_code == 400
    assert response.json()["error"] == "EMPTY_RECORDS"

def test_upload_department_master_unexpected_failure():
    payload = {
        "records": [
            {
                "office": "Revenue Head Office",
                "division_section": "Taxes Section",
                "sub_section": "Direct Taxes",
                "user": "officer_revenue_1"
            }
        ],
        "department": "trigger_failure"
    }
    response = client.post("/api/v1/upload/department-mapping-master", json=payload)
    assert response.status_code == 500
    assert "Simulated DB write failure" in response.json()["error"]

def test_get_department_master_success():
    # Seed revenue mapping first in db
    db = TestingSessionLocal()
    from src.db.models import DepartmentMappingMaster
    db.add(DepartmentMappingMaster(
        office="Revenue Head Office",
        division_section="Taxes Section",
        sub_section="Direct Taxes",
        department="revenue",
        user="officer_revenue_1",
        uploaded_at="2026-06-20T12:00:00Z"
    ))
    db.commit()
    db.close()

    response = client.get("/api/v1/department-mapping-master?department=revenue")
    assert response.status_code == 200
    json_data = response.json()
    assert len(json_data["data"]["records"]) >= 1
    assert json_data["data"]["records"][0]["department"] == "revenue"
    assert json_data["error"] is None

def test_get_department_master_not_found():
    response = client.get("/api/v1/department-mapping-master?department=not_found")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["data"]["records"] == []
    assert json_data["error"] is None

def test_get_department_master_validation_error():
    response = client.get("/api/v1/department-mapping-master?department=")
    assert response.status_code == 400
    assert response.json()["error"] == "EMPTY_DEPARTMENT"

def test_get_department_master_unexpected_failure():
    response = client.get("/api/v1/department-mapping-master?department=trigger_failure")
    assert response.status_code == 500
    json_data = response.json()
    assert json_data["data"] == []
    assert "Simulated DB read failure" in json_data["error"]

# ----------------- NEW API FLOWS TESTS -----------------

def test_generate_initial_suggestion_success():
    payload = {
        "rti_query": "Please provide direct taxes zoning classification information."
    }
    response = client.post("/api/v1/generate_initial_suggestion", json=payload)
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["data"]["results"]["suggestion"] is not None
    assert "Action Plan" in json_data["data"]["results"]["suggestion"]
    assert json_data["error"] is None

def test_generate_initial_suggestion_validation_error():
    payload = {
        "rti_query": "   "
    }
    response = client.post("/api/v1/generate_initial_suggestion", json=payload)
    assert response.status_code == 400
    assert response.json()["error"] == "EMPTY_RTI_QUERY"

def test_retrieve_chat_context_success():
    payload = {
        "rti_query": "Please provide direct taxes zoning classification information.",
        "suggested_flow": "1. Verify details, 2. Routing, 3. Draft reply.",
        "user_chat_query": "Which zone is revenue head office located in?"
    }
    response = client.post("/api/v1/retrieve_chat_context", json=payload)
    assert response.status_code == 200
    json_data = response.json()
    assert "refined_results" in json_data["data"]
    assert isinstance(json_data["data"]["refined_results"], list)
    assert json_data["message"] is not None
    assert "Based on the conversation state" in json_data["message"]
    assert json_data["error"] is None

def test_retrieve_chat_context_validation_error():
    # Empty rti_query
    payload = {
        "rti_query": "",
        "suggested_flow": "some flow",
        "user_chat_query": "some query"
    }
    response = client.post("/api/v1/retrieve_chat_context", json=payload)
    assert response.status_code == 400
    assert response.json()["error"] == "EMPTY_RTI_QUERY"

    # Empty suggested_flow
    payload = {
        "rti_query": "some query",
        "suggested_flow": " ",
        "user_chat_query": "some query"
    }
    response = client.post("/api/v1/retrieve_chat_context", json=payload)
    assert response.status_code == 400
    assert response.json()["error"] == "EMPTY_SUGGESTED_FLOW"

    # Empty user_chat_query
    payload = {
        "rti_query": "some query",
        "suggested_flow": "some flow",
        "user_chat_query": ""
    }
    response = client.post("/api/v1/retrieve_chat_context", json=payload)
    assert response.status_code == 400
    assert response.json()["error"] == "EMPTY_USER_CHAT_QUERY"

def test_mask_and_index_completed_rti_success():
    # Seed a test record to close
    db = TestingSessionLocal()
    from src.db.models import RtiQuery
    test_query = RtiQuery(
        rti_query_id="query_to_close",
        inward_id="inward_close_test",
        query_text="RTI query content by Mr. John Doe",
        department_id=1,
        status_id=1
    )
    db.add(test_query)
    db.commit()
    db.close()

    payload = {
        "inward_id": "inward_close_test",
        "rti_query": "RTI query content by Mr. John Doe",
        "office_note": "Case completed on 2026-06-22 by Officer Ram Prasad."
    }
    response = client.post("/api/v1/mask_and_index_completed_rti", json=payload)
    assert response.status_code == 200
    assert response.json()["error"] is None
    assert "PII masked and RTI index updated successfully" in response.json()["message"]

    # Verify database was updated
    db = TestingSessionLocal()
    closed_query = db.query(RtiQuery).filter(RtiQuery.inward_id == "inward_close_test").first()
    assert closed_query.status_id == 3
    assert len(closed_query.office_notes) >= 1
    assert closed_query.office_notes[0].office_note == "Case completed on 2026-06-22 by Officer Ram Prasad."
    db.close()

def test_mask_and_index_completed_rti_validation_error():
    # Empty inward_id
    payload = {
        "inward_id": "  ",
        "rti_query": "query",
        "office_note": "note"
    }
    response = client.post("/api/v1/mask_and_index_completed_rti", json=payload)
    assert response.status_code == 400
    assert response.json()["error"] == "EMPTY_INWARD_ID"

    # Empty rti_query
    payload = {
        "inward_id": "inward_123",
        "rti_query": "",
        "office_note": "note"
    }
    response = client.post("/api/v1/mask_and_index_completed_rti", json=payload)
    assert response.status_code == 400
    assert response.json()["error"] == "EMPTY_RTI_QUERY"

    # Empty office_note
    payload = {
        "inward_id": "inward_123",
        "rti_query": "query",
        "office_note": "   "
    }
    response = client.post("/api/v1/mask_and_index_completed_rti", json=payload)
    assert response.status_code == 400
    assert response.json()["error"] == "EMPTY_OFFICE_NOTE"

def test_mask_and_index_completed_rti_not_found():
    payload = {
        "inward_id": "non_existent_inward_id",
        "rti_query": "query",
        "office_note": "note"
    }
    response = client.post("/api/v1/mask_and_index_completed_rti", json=payload)
    assert response.status_code == 404
    assert response.json()["error"] == "RECORD_NOT_FOUND"

def test_mask_and_index_completed_rti_already_closed():
    # Seed a query that is already Resolved (status_id = 3)
    db = TestingSessionLocal()
    from src.db.models import RtiQuery
    test_query = RtiQuery(
        rti_query_id="query_already_closed",
        inward_id="inward_closed_test",
        query_text="RTI query text",
        department_id=1,
        status_id=3
    )
    db.add(test_query)
    db.commit()
    db.close()

    payload = {
        "inward_id": "inward_closed_test",
        "rti_query": "query",
        "office_note": "note"
    }
    response = client.post("/api/v1/mask_and_index_completed_rti", json=payload)
    assert response.status_code == 404
    assert response.json()["error"] == "ALREADY_CLOSED"

def test_mask_and_index_completed_rti_llm_error():
    # Seed a test record
    db = TestingSessionLocal()
    from src.db.models import RtiQuery
    test_query = RtiQuery(
        rti_query_id="query_llm_error",
        inward_id="inward_llm_error",
        query_text="RTI query text",
        department_id=1,
        status_id=1
    )
    db.add(test_query)
    db.commit()
    db.close()

    payload = {
        "inward_id": "inward_llm_error",
        "rti_query": "trigger_llm_error text",
        "office_note": "note"
    }
    response = client.post("/api/v1/mask_and_index_completed_rti", json=payload)
    assert response.status_code == 522
    assert response.json()["error"] == "LLM_ERROR"

if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__]))
