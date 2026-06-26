import uuid
from typing import List, Optional
from sqlalchemy.orm import Session
from src.db.models import RtiQuery, StatusLookup, OfficeNote, SupportingDocument, UserQuery, AtomicQuery, DepartmentMappingMaster
from src.schema.query_schema import (
    RtiQueryItem, RtiQueryCountData, OfficeNoteItem, RtiQueryDetailData , MarkAtomicQueryRequest
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
            
            import base64
            collated_base64 = None
            if query_obj.collated_office_note:
                collated_base64 = base64.b64encode(query_obj.collated_office_note).decode('utf-8')
            
            return [
                RtiQueryItem(
                    rti_query_id=query_obj.rti_query_id,
                    query=query_obj.rti_query or query_obj.query_text or "",
                    status=query_obj.status.status_label,
                    remark=query_obj.remark,
                    collated_office_note=collated_base64
                )
            ]
        
        # List mode
        query = db.query(RtiQuery)
        
        # Apply filters
        if status_id is not None:
            query = query.filter(RtiQuery.status_id == status_id)
            
        if assigned_to is not None:
            # Since assigned_to was removed from RtiQuery, no records can match this filter.
            return []
            
        # if unassigned_only is True, all queries are effectively unassigned since assigned_to column doesn't exist
        
        # Apply pagination
        results = query.offset(offset).limit(limit).all()
        
        import base64
        return [
            RtiQueryItem(
                rti_query_id=q.rti_query_id,
                query=q.rti_query or q.query_text or "",
                status=q.status.status_label,
                remark=q.remark,
                collated_office_note=base64.b64encode(q.collated_office_note).decode('utf-8') if q.collated_office_note else None
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
            
        # Get details from associated AtomicQuery if it exists
        atomic = db.query(AtomicQuery).filter(AtomicQuery.rti_query_id == rti_query_id).first()
        inward_id = atomic.inward_id if atomic else "N/A"
        query_text = atomic.atomic_query if atomic else (q.rti_query or "")
        department_id = atomic.department_id if atomic else 0
        
        # Sort notes newest first
        sorted_notes = sorted(q.office_notes, key=lambda x: x.created_at, reverse=True)
        
        return RtiQueryDetailData(
            rti_query_id=q.rti_query_id,
            inward_id=inward_id,
            query_text=query_text,
            department_id=department_id,
            status=q.status.status_label,
            assigned_to=None,
            assigned_at=None,
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
                "enclosure_id": aq.enclosure_id,
                "status_id":aq.status_id
            } for aq, dept in results
        ]

    @staticmethod
    def fetch_atomic_query_office_notes(db: Session, rti_query_id: str) -> list:
        import base64
        print("RTI_QUERY_ID : ",rti_query_id)
        results = db.query(AtomicQuery).filter(AtomicQuery.rti_query_id == rti_query_id).all()
        
        notes_data = []
        for aq in results:
            note_base64 = None
            note_text = None
            if aq.atomic_query_office_note:
                note_base64 = base64.b64encode(aq.atomic_query_office_note).decode('utf-8')
                try:
                    note_text = aq.atomic_query_office_note.decode('utf-8', errors='ignore')
                except Exception:
                    note_text = None
            
            notes_data.append({
                "atomic_query_id": aq.atomic_query_id,
                "atomic_query": aq.atomic_query,
                "department_id": aq.department_id,
                "office_note_base64": note_base64,
                "atomic_query_office_note": note_text,
            })
            print("NOTES : ",notes_data)
        return notes_data

    @staticmethod
    def update_rti_query(
        db: Session,
        rti_query_id: str,
        status_id: Optional[int] = None,
        remark: Optional[str] = None,
        collated_office_note: Optional[bytes] = None,
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

            if collated_office_note is not None:
                rti_query.collated_office_note = collated_office_note

            db.commit()
            return {"success": True, "message": "RTI Query updated successfully"}
        except Exception as e:
            print("UPdate Exception: ",e)
            db.rollback()
            return {"success": False, "message": f"Failed to update RTI query: {str(e)}", "error": "UPDATE_FAILED"}

    @staticmethod
    def update_atomic_query(
        db: Session,
        atomic_query_id: str,
        atomic_query_office_note: Optional[bytes] = None,
        updated_by: str = "System"
    ) -> dict:
        try:
            atomic_query = db.query(AtomicQuery).filter(AtomicQuery.atomic_query_id == atomic_query_id).first()
            if not atomic_query:
                return {"success": False, "message": "Atomic Query not found", "error": "NOT_FOUND"}

            if atomic_query_office_note is not None:
                atomic_query.atomic_query_office_note = atomic_query_office_note

            db.commit()
            return {"success": True, "message": "Atomic Query updated successfully"}
        except Exception as e:
            db.rollback()
            return {"success": False, "message": f"Failed to update Atomic Query: {str(e)}", "error": "UPDATE_FAILED"}

    @staticmethod
    def mark_atomic_query(db: Session, request: MarkAtomicQueryRequest) -> dict:
        from src.utils.kafka_producer import publish_draft_event
        try:
            atomic_query = db.query(AtomicQuery).filter(AtomicQuery.atomic_query_id == request.atomic_query_id).first()
            if not atomic_query:
                return {"success": False, "message": "Atomic Query not found", "error": "NOT_FOUND"}

            # Status 3 means mark off is done
            atomic_query.status_id = 3
            db.flush() # Ensure the status update is visible in the current session

            # Check if all atomic queries related to this RTI query are completed (status_id == 3)
            all_atomic_queries = db.query(AtomicQuery).filter(AtomicQuery.rti_query_id == atomic_query.rti_query_id).all()
            all_completed = all(aq.status_id == 3 for aq in all_atomic_queries)

            if all_completed:
                # Add message to kafka to create a draft
                kafka_payload = {
                    "rti_id": atomic_query.rti_query_id
                }
                
                publish_success = publish_draft_event(kafka_payload)
                if not publish_success:
                    print(f"Warning: Failed to publish draft event for atomic_query_id: {request.atomic_query_id}")
                message = "Atomic Query marked off and draft event published"
            else:
                message = "Atomic Query marked off successfully (waiting for other atomic queries to complete)"

            db.commit()
            return {"success": True, "message": message}
        except Exception as e:
            db.rollback()
            return {"success": False, "message": f"Failed to mark off Atomic Query: {str(e)}", "error": "MARK_FAILED"}
