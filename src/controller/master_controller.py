from fastapi import status, Query
from fastapi.responses import JSONResponse

from src.schema.master_schema import UploadDepartmentMasterRequest
from src.service.master_service import MasterService

class MasterController:
    @staticmethod
    def upload_department_master(request: UploadDepartmentMasterRequest):
        if not request.department.strip():
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "data": [],
                    "message": "department cannot be empty",
                    "error": "EMPTY_DEPARTMENT"
                }
            )
        if not request.records:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "data": [],
                    "message": "records list cannot be empty",
                    "error": "EMPTY_RECORDS"
                }
            )

        try:
            data = MasterService.upload_department_master(request)
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "data": [item.model_dump() for item in data],
                    "message": "Department master uploaded successfully",
                    "error": None
                }
            )
        except Exception as e:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "data": [],
                    "message": "Unexpected failure occurred",
                    "error": str(e)
                }
            )

    @staticmethod
    def get_department_master(
        department: str = Query(..., description="Filter based on department")
    ):
        if not department.strip():
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "data": None,
                    "message": "department query parameter cannot be empty",
                    "error": "EMPTY_DEPARTMENT"
                }
            )

        try:
            data = MasterService.get_department_master(department)
            if data is None:
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={
                        "data": {
                            "records": []
                        },
                        "message": "No department mapping found",
                        "error": None
                    }
                )
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "data": data.model_dump(),
                    "message": "Department master retrieved successfully",
                    "error": None
                }
            )
        except Exception as e:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "data": [],
                    "message": "Unexpected failure occurred",
                    "error": str(e)
                }
            )
