from typing import Optional
from pydantic import BaseModel, Field

class InwardCreateRequest(BaseModel):
    department_id: int
    division_id: int
    sub_section_id: int
    case_access_level_id: int
    privacy_level_id: int
    inward_priority_id: int
    year: int

class InwardCreateResponseData(BaseModel):
    inward_id: str

class InwardDetailData(BaseModel):
    inward_id: str
    department_id: int
    division_id: int
    sub_section_id: int
    case_access_level_id: int
    privacy_level_id: int
    inward_priority_id: int
    year: int
    status: str
    rti_query_id: Optional[str] = None
    created_at: str
    created_by: str

class OfficeNoteCreateRequest(BaseModel):
    inward_id: str
    office_note: str = Field(..., max_length=5000)

class OfficeNoteCreateResponseData(BaseModel):
    office_note_id: str

class OfficeNoteDetailData(BaseModel):
    office_note_id: str
    inward_id: str
    office_note: str
    created_at: str
    created_by: str
