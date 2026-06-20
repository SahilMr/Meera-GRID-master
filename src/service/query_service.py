from typing import List, Optional
from datetime import datetime
from src.schema.query_schema import (
    RtiQueryItem, RtiQueryCountData, OfficeNoteItem, RtiQueryDetailData
)

STATUS_LOOKUP = {
    1: "Pending",
    2: "In Progress",
    3: "Resolved"
}

class QueryService:
    @staticmethod
    def fetch_rti_queries(
        status_id: Optional[int] = None,
        limit: int = 20,
        offset: int = 0,
        rti_query_id: Optional[str] = None,
        assigned_to: Optional[str] = None,
        unassigned_only: bool = False
    ) -> List[RtiQueryItem]:
        # Single-record mode
        if rti_query_id is not None:
            if rti_query_id == "not_found":
                return []
            
            return [
                RtiQueryItem(
                    rti_query_id=rti_query_id,
                    inward_id="mock_inward_uuid_1",
                    query="Mock single query content",
                    department_id=1,
                    status="Pending",
                    assigned_to=assigned_to or "mock_user",
                    assigned_at="2026-06-20T12:00:00Z"
                )
            ]
        
        # List mode
        mock_queries = [
            RtiQueryItem(
                rti_query_id="query_1",
                inward_id="mock_inward_uuid_1",
                query="First mock query content",
                department_id=1,
                status="Pending",
                assigned_to=None,
                assigned_at=None
            ),
            RtiQueryItem(
                rti_query_id="query_2",
                inward_id="mock_inward_uuid_2",
                query="Second mock query content",
                department_id=2,
                status="Resolved",
                assigned_to="officer_1",
                assigned_at="2026-06-20T10:00:00Z"
            )
        ]
        
        # Apply filters
        filtered = mock_queries
        if status_id is not None:
            status_label = STATUS_LOOKUP.get(status_id)
            filtered = [q for q in filtered if q.status == status_label]
            
        if assigned_to is not None:
            filtered = [q for q in filtered if q.assigned_to == assigned_to]
            
        if unassigned_only:
            filtered = [q for q in filtered if q.assigned_to is None]
            
        # Apply pagination
        return filtered[offset : offset + limit]

    @staticmethod
    def fetch_rti_query_count() -> RtiQueryCountData:
        return RtiQueryCountData(
            total_count=2,
            pending_count=1,
            resolved_count=1
        )

    @staticmethod
    def fetch_rti_query_detail(rti_query_id: str) -> Optional[RtiQueryDetailData]:
        if rti_query_id == "not_found":
            return None
            
        return RtiQueryDetailData(
            rti_query_id=rti_query_id,
            inward_id="mock_inward_uuid_1",
            query_text="This is detailed mock query text.",
            department_id=1,
            status="Pending",
            assigned_to="officer_1",
            assigned_at="2026-06-20T10:00:00Z",
            supporting_documents=["doc_1_url", "doc_2_url"],
            office_notes=[
                OfficeNoteItem(
                    office_note_id="note_2",
                    office_note="Updated discussion on the query.",
                    created_at="2026-06-20T12:00:00Z",
                    created_by="admin"
                ),
                OfficeNoteItem(
                    office_note_id="note_1",
                    office_note="Initial review of the query.",
                    created_at="2026-06-20T10:00:00Z",
                    created_by="officer"
                )
            ]
        )
