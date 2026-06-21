from typing import Optional
from fastapi import Query, Path, Body, status, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from src.schema.common_schema import ApiResponse
from src.schema.query_schema import RtiQueryCreateRequest, AtomicQueryCreateRequest
from src.service.query_service import QueryService
from src.db.database import get_db

class QueryController:
    # @staticmethod
    # def fetch_rti_query(
    #     status_id: Optional[int] = Query(None, description="Filter by status ID"),
    #     limit: int = Query(20, ge=1, le=100, description="Pagination limit"),
    #     offset: int = Query(0, ge=0, description="Pagination offset"),
    #     rti_query_id: Optional[str] = Query(None, description="Specific RTI query ID"),
    #     assigned_to: Optional[str] = Query(None, description="Filter by assigned user"),
    #     unassigned_only: bool = Query(False, description="Filter to unassigned queries only"),
    #     db: Session = Depends(get_db)
    # ):
    #     # Validation: 400 if unassigned_only is combined with assigned_to
    #     if unassigned_only and assigned_to:
    #         return JSONResponse(
    #             status_code=status.HTTP_400_BAD_REQUEST,
    #             content={
    #                 "data": [],
    #                 "message": "Cannot combine assigned_to filter with unassigned_only",
    #                 "error": "INVALID_FILTER_COMBINATION"
    #             }
    #         )

    #     # Validation: status_id must be in [1, 2, 3] if provided
    #     if status_id is not None and status_id not in [1, 2, 3]:
    #         return JSONResponse(
    #             status_code=status.HTTP_400_BAD_REQUEST,
    #             content={
    #                 "data": [],
    #                 "message": f"Invalid status_id: {status_id}",
    #                 "error": "INVALID_STATUS_ID"
    #             }
    #         )

    #     # Fetch records from service
    #     records = QueryService.fetch_rti_queries(
    #         db=db,
    #         status_id=status_id,
    #         limit=limit,
    #         offset=offset,
    #         rti_query_id=rti_query_id,
    #         assigned_to=assigned_to,
    #         unassigned_only=unassigned_only
    #     )

    #     if rti_query_id is not None and not records:
    #         return JSONResponse(
    #             status_code=status.HTTP_200_OK,
    #             content={
    #                 "data": [],
    #                 "message": "No record found",
    #                 "error": None
    #             }
    #         )

    #     return JSONResponse(
    #         status_code=status.HTTP_200_OK,
    #         content={
    #             "data": [r.model_dump() for r in records],
    #             "message": "Queries fetched successfully",
    #             "error": None
    #         }
    #     )

    # @staticmethod
    # def fetch_rti_query_count(db: Session = Depends(get_db)):
    #     try:
    #         data = QueryService.fetch_rti_query_count(db)
    #         return JSONResponse(
    #             status_code=status.HTTP_200_OK,
    #             content={
    #                 "data": data.model_dump(),
    #                 "message": "Counts retrieved successfully",
    #                 "error": None
    #             }
    #         )
    #     except Exception as e:
    #         return JSONResponse(
    #             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    #             content={
    #                 "data": None,
    #                 "message": "Failed to fetch counts",
    #                 "error": str(e)
    #             }
    #         )

    # @staticmethod
    # def fetch_rti_query_detail(
    #     rti_query_id: str = Path(..., description="The query ID"),
    #     db: Session = Depends(get_db)
    # ):
    #     detail = QueryService.fetch_rti_query_detail(db, rti_query_id)
    #     if detail is None:
    #         return JSONResponse(
    #             status_code=status.HTTP_404_NOT_FOUND,
    #             content={
    #                 "data": None,
    #                 "message": f"RTI query {rti_query_id} not found",
    #                 "error": "RTI_QUERY_NOT_FOUND"
    #             }
    #         )
    #     return JSONResponse(
    #         status_code=status.HTTP_200_OK,
    #         content={
    #             "data": detail.model_dump(),
    #             "message": "Query detail retrieved successfully",
    #             "error": None
    #         }
    #     )

    @staticmethod
    def create_rti_query(
        request: RtiQueryCreateRequest = Body(...),
        db: Session = Depends(get_db)
    ):
        result = QueryService.create_rti_query(
            db=db,
            rti_query_id=request.rti_query_id,
            rti_query=request.rti_query,
            applicant_name=request.applicant_name,
            applicant_email=request.applicant_email,
            applicant_phone_number=request.applicant_phone_number,
            status_id=request.status_id
        )
        
        if result["success"]:
            return JSONResponse(
                status_code=status.HTTP_201_CREATED,
                content={
                    "data": {"rti_query_id": result.get("rti_query_id")},
                    "message": result["message"],
                    "error": None
                }
            )
        else:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "data": None,
                    "message": result["message"],
                    "error": "CREATE_FAILED"
                }
            )

    @staticmethod
    def insert_atomic_query(
        request: AtomicQueryCreateRequest = Body(...),
        db: Session = Depends(get_db)
    ):
        result = QueryService.insert_atomic_query(
            db=db,
            rti_query_id=request.rti_query_id,
            atomic_query=request.atomic_query,
            department_id=request.department_id,
            inward_id=request.inward_id,
            office_note_id=request.office_note_id,
            enclosure_id=request.enclosure_id
        )
        
        if result["success"]:
            return JSONResponse(
                status_code=status.HTTP_201_CREATED,
                content={
                    "data": {"atomic_query_id": result.get("atomic_query_id")},
                    "message": result["message"],
                    "error": None
                }
            )
        else:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "data": None,
                    "message": result["message"],
                    "error": "INSERT_FAILED"
                }
            )
