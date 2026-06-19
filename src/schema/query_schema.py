from typing import List, Optional
from pydantic import BaseModel

class RtiQueryItem(BaseModel):
    rti_query_id: str
    inward_id: str
    query: str
    department_id: int
    status: str
    assigned_to: Optional[str] = None
    assigned_at: Optional[str] = None

class RtiQueryCountData(BaseModel):
    total_count: int
    pending_count: int
    resolved_count: int

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

class AssignRtiQueryResponseData(BaseModel):
    rti_query_id: str
    assigned_to: str
    assigned_at: str
