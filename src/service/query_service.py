import uuid
from typing import List, Optional
from sqlalchemy.orm import Session
from src.db.models import RtiQuery, StatusLookup, OfficeNote, SupportingDocument, UserQuery, AtomicQuery, DepartmentMappingMaster
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
                    query=query_obj.rti_query or query_obj.query_text or "",
                    status=query_obj.status.status_label,
                    remark=query_obj.remark
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
                query=q.rti_query or q.query_text or "",
                status=q.status.status_label,
                remark=q.remark
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

    @staticmethod
    def create_rti_query(
        db: Session,
        rti_query_id: str,
        rti_query: str,
        applicant_name: str,
        applicant_email: str,
        applicant_phone_number: str,
        status_id: int
    ) -> dict:
        try:
            new_query = RtiQuery(
                rti_query_id=rti_query_id,
                rti_query=rti_query,
                applicant_name=applicant_name,
                applicant_email=applicant_email,
                applicant_phone_number=applicant_phone_number,
                status_id=status_id
            )
            db.add(new_query)
            db.commit()
            return {"success": True, "message": "RTI query created successfully", "rti_query_id": new_query.rti_query_id}
        except Exception as e:
            db.rollback()
            return {"success": False, "message": f"Failed to create RTI query: {str(e)}"}

    @staticmethod
    def insert_atomic_query(
        db: Session,
        rti_query_id: str,
        atomic_query: str,
        department_id: Optional[str] = None,
        inward_id: Optional[str] = None,
        office_note_id: Optional[str] = None,
        enclosure_id: Optional[str] = None
    ) -> dict:
        try:
            dept_id = None
            if department_id is not None:
                try:
                    dept_id = int(department_id)
                except ValueError:
                    pass

            new_atomic = AtomicQuery(
                atomic_query_id=str(uuid.uuid4()),
                rti_query_id=rti_query_id,
                atomic_query=atomic_query,
                department_id=dept_id,
                inward_id=inward_id,
                office_note_id=office_note_id,
                enclosure_id=enclosure_id
            )
            db.add(new_atomic)
            db.commit()
            return {"success": True, "message": "Atomic query created successfully", "atomic_query_id": new_atomic.atomic_query_id}
        except Exception as e:
            db.rollback()
            return {"success": False, "message": f"Failed to insert atomic query: {str(e)}"}

    @staticmethod
    def get_atomic_queries(
        db: Session,
        rti_query_id: str,
        department_mapping_id: Optional[str] = None
    ) -> List[dict]:
        query = db.query(AtomicQuery, DepartmentMappingMaster).outerjoin(
            DepartmentMappingMaster, AtomicQuery.department_id == DepartmentMappingMaster.id
        ).filter(AtomicQuery.rti_query_id == rti_query_id)
       
        if department_mapping_id:
            query = query.filter(DepartmentMappingMaster.id == department_mapping_id)
            
        results = query.all()
        
        return [
            {
                "atomic_query_id": aq.atomic_query_id,
                "rti_query_id": aq.rti_query_id,
                "atomic_query": aq.atomic_query,
                "department_id": aq.department_id,
                "department_name": dept.department if dept else None,
                "inward_id": aq.inward_id,
                "office_note_id": aq.office_note_id,
                "enclosure_id": aq.enclosure_id
            } for aq, dept in results
        ]

    @staticmethod
    def update_rti_query(
        db: Session,
        rti_query_id: str,
        status_id: Optional[int] = None,
        remark: Optional[str] = None,
        updated_by: str = "System"
    ) -> dict:
        import datetime
        try:
            rti_query = db.query(RtiQuery).filter(RtiQuery.rti_query_id == rti_query_id).first()
            if not rti_query:
                return {"success": False, "message": "RTI Query not found", "error": "NOT_FOUND"}

            if status_id is not None:
                status_exists = db.query(StatusLookup).filter(StatusLookup.status_id == status_id).first()
                if not status_exists:
                    return {"success": False, "message": "Invalid status ID", "error": "INVALID_STATUS"}
                rti_query.status_id = status_id

            if remark is not None:
                rti_query.remark = remark

            db.commit()
            return {"success": True, "message": "RTI Query updated successfully"}
        except Exception as e:
            db.rollback()
            return {"success": False, "message": f"Failed to update RTI query: {str(e)}", "error": "UPDATE_FAILED"}
