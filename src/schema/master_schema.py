from typing import List, Optional
from pydantic import BaseModel

# upload_department_master API
class UploadRecordItem(BaseModel):
    office: str
    division_section: str
    sub_section: str
    user: str

class UploadDepartmentMasterRequest(BaseModel):
    records: List[UploadRecordItem]
    department: str

class UploadDepartmentMasterResponseData(BaseModel):
    upload_status: str
    total_records_uploaded: str

# get_department_master API
class GetDepartmentMasterRecord(BaseModel):
    id: int
    office: str
    division_section: str
    sub_section: str
    department: str
    user: str

class GetDepartmentMasterResponseData(BaseModel):
    records: List[GetDepartmentMasterRecord]
