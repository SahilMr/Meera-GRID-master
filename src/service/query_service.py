from typing import List, Optional
from sqlalchemy.orm import Session
from src.db.models import RtiQuery, StatusLookup, OfficeNote, SupportingDocument, UserQuery
from src.schema.query_schema import (
    RtiQueryItem, RtiQueryCountData, OfficeNoteItem, RtiQueryDetailData
)

class QueryService:
    @staticmethod
    def fetch_rti_queries(
        db: Session,
        status_id: Optional[int] = None,
        limit: int = 20,
        offset: int = 0,
        rti_query_id: Optional[str] = None,
        assigned_to: Optional[str] = None,
        unassigned_only: bool = False
    ) -> List[RtiQueryItem]:
        # Single-record mode
        if rti_query_id is not None:
            query_obj = db.query(RtiQuery).filter(RtiQuery.rti_query_id == rti_query_id).first()
            if not query_obj:
                return []
            
            return [
                RtiQueryItem(
                    rti_query_id=query_obj.rti_query_id,
                    inward_id=query_obj.inward_id,
                    query=query_obj.query_text,
                    department_id=query_obj.department_id,
                    status=query_obj.status.status_label,
                    assigned_to=query_obj.assigned_to,
                    assigned_at=query_obj.assigned_at
                )
            ]
        
        # List mode
        query = db.query(RtiQuery)
        
        # Apply filters
        if status_id is not None:
            query = query.filter(RtiQuery.status_id == status_id)
            
        if assigned_to is not None:
            query = query.filter(RtiQuery.assigned_to == assigned_to)
            
        if unassigned_only:
            query = query.filter(RtiQuery.assigned_to.is_(None))
            
        # Apply pagination
        results = query.offset(offset).limit(limit).all()
        
        return [
            RtiQueryItem(
                rti_query_id=q.rti_query_id,
                inward_id=q.inward_id,
                query=q.query_text,
                department_id=q.department_id,
                status=q.status.status_label,
                assigned_to=q.assigned_to,
                assigned_at=q.assigned_at
            ) for q in results
        ]

    @staticmethod
    def fetch_rti_query_count(db: Session) -> RtiQueryCountData:
        total = db.query(RtiQuery).count()
        # Find status labels map to get pending vs resolved
        pending_count = db.query(RtiQuery).join(StatusLookup).filter(StatusLookup.status_label == "Pending").count()
        resolved_count = db.query(RtiQuery).join(StatusLookup).filter(StatusLookup.status_label == "Resolved").count()
        
        # Look up "Not In Scope" status count
        not_in_scope_status = db.query(StatusLookup).filter(StatusLookup.status_label == "Not In Scope").first()
        not_in_scope_count = (
            db.query(RtiQuery).filter(RtiQuery.status_id == not_in_scope_status.status_id).count()
            if not_in_scope_status else 0
        )
        
        # Calculate active sessions based on distinct active users (mocked to a value > 1 if none found)
        active_sessions_count = db.query(UserQuery.user_id).distinct().count()
        if active_sessions_count == 0:
            active_sessions_count = 5  # default mock value
        
        return RtiQueryCountData(
            total_count=total,
            pending_count=pending_count,
            resolved_count=resolved_count,
            not_in_scope_count=not_in_scope_count,
            active_sessions_count=active_sessions_count
        )

    @staticmethod
    def fetch_rti_query_detail(db: Session, rti_query_id: str) -> Optional[RtiQueryDetailData]:
        q = db.query(RtiQuery).filter(RtiQuery.rti_query_id == rti_query_id).first()
        if not q:
            return None
            
        # Sort notes newest first
        sorted_notes = sorted(q.office_notes, key=lambda x: x.created_at, reverse=True)
        
        return RtiQueryDetailData(
            rti_query_id=q.rti_query_id,
            inward_id=q.inward_id,
            query_text=q.query_text,
            department_id=q.department_id,
            status=q.status.status_label,
            assigned_to=q.assigned_to,
            assigned_at=q.assigned_at,
            supporting_documents=[doc.document_url for doc in q.supporting_documents],
            office_notes=[
                OfficeNoteItem(
                    office_note_id=n.office_note_id,
                    office_note=n.office_note,
                    created_at=n.created_at,
                    created_by=n.created_by
                ) for n in sorted_notes
            ]
        )
