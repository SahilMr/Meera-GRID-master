from typing import List, Optional
from pydantic import BaseModel

class RtiQueryItem(BaseModel):
    rti_query_id: str
    query: str
    status: str
    remark: Optional[str] = None
    
class RtiQueryCountData(BaseModel):
    total_count: int
    pending_count: int
    resolved_count: int
    not_in_scope_count: int
    active_sessions_count: int

class OfficeNoteItem(BaseModel):
    office_note_id: str
    office_note: str
    created_at: str
    created_by: str

class RtiQueryDetailData(BaseModel):
    rti_query_id: str
    inward_id: str
    query_text: str
    department_id: int
    status: str
    assigned_to: Optional[str] = None
    assigned_at: Optional[str] = None
    supporting_documents: List[str]
    office_notes: List[OfficeNoteItem]

class RtiQueryCreateRequest(BaseModel):
    rti_query_id: str
    rti_query: str
    applicant_name: str
    applicant_email: str
    applicant_phone_number: str
    status_id: int

class AtomicQueryCreateRequest(BaseModel):
    rti_query_id: str
    atomic_query: str
    department_id: str
    inward_id: Optional[str] = None
    office_note_id: Optional[str] = None
    enclosure_id: Optional[str] = None
