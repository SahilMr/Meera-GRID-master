from typing import List, Optional
from src.schema.master_schema import (
    UploadDepartmentMasterRequest, UploadDepartmentMasterResponseData,
    GetDepartmentMasterRecord, GetDepartmentMasterResponseData
)

class MasterService:
    @staticmethod
    def upload_department_master(request: UploadDepartmentMasterRequest) -> List[UploadDepartmentMasterResponseData]:
        if request.department == "trigger_failure":
            raise Exception("Simulated DB write failure")
            
        total_count = len(request.records)
        return [
            UploadDepartmentMasterResponseData(
                upload_status="success",
                total_records_uploaded=str(total_count)
            )
        ]

    @staticmethod
    def get_department_master(department: str) -> Optional[GetDepartmentMasterResponseData]:
        if department == "trigger_failure":
            raise Exception("Simulated DB read failure")
        if department == "not_found":
            return None
            
        return GetDepartmentMasterResponseData(
            records=[
                GetDepartmentMasterRecord(
                    office="Head Office",
                    division_section="Revenue Division",
                    sub_section="Section A",
                    department=department,
                    user="officer_1"
                )
            ]
        )
