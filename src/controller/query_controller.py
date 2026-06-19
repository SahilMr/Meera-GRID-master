from typing import Optional
from fastapi import Query, Path, status
from fastapi.responses import JSONResponse

from src.schema.common_schema import ApiResponse
from src.schema.query_schema import (
    RtiQueryItem, RtiQueryCountData, RtiQueryDetailData, AssignRtiQueryResponseData
)
from src.service.query_service import QueryService

class QueryController:
    @staticmethod
    def fetch_rti_query(
        status_id: Optional[int] = Query(None, description="Filter by status ID"),
        limit: int = Query(20, ge=1, le=100, description="Pagination limit"),
        offset: int = Query(0, ge=0, description="Pagination offset"),
        rti_query_id: Optional[str] = Query(None, description="Specific RTI query ID"),
        assigned_to: Optional[str] = Query(None, description="Filter by assigned user"),
        unassigned_only: bool = Query(False, description="Filter to unassigned queries only")
    ):
        # Validation: 400 if unassigned_only is combined with assigned_to
        if unassigned_only and assigned_to:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "data": [],
                    "message": "Cannot combine assigned_to filter with unassigned_only",
                    "error": "INVALID_FILTER_COMBINATION" 
                }
            )

        # Validation: If status_id is provided but invalid/non-existent.
        # Let's say valid status_ids are in [1, 2, 3]. If status_id is outside, return 400.
        if status_id is not None and status_id not in [1, 2, 3]:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "data": [],
                    "message": f"Invalid status_id: {status_id}",
                    "error": "INVALID_STATUS_ID"
                }
            )

        # Single-record mode
        if rti_query_id is not None:
            # Let's mock a simple check. If query_id is "not_found", return empty list.
            if rti_query_id == "not_found":
                return ApiResponse(
                    data=[],
                    message="No record found",
                    error=None
                )
            # Standard single element list mode
            # Since first version should return empty response, let's return data: [] as default
            # or a list with an empty/mock item if they wanted real data.
            # "make sure all APIs return empty responses, theres not logic as such yet."
            return ApiResponse(
                data=[],
                message="No record found",
                error=None
            )

        # List mode
        data = QueryService.fetch_rti_queries(
            status_id=status_id,
            limit=limit,
            offset=offset,
            rti_query_id=rti_query_id,
            assigned_to=assigned_to,
            unassigned_only=unassigned_only
        )
        return ApiResponse(
            data=data,
            message="Queries fetched successfully",
            error=None
        )

    @staticmethod
    def fetch_rti_query_count():
        try:
            data = QueryService.fetch_rti_query_count()
            return ApiResponse(
                data=data,
                message="Counts retrieved successfully",
                error=None
            )
        except Exception as e:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "data": None,
                    "message": "Failed to fetch counts",
                    "error": str(e)
                }
            )

    @staticmethod
    def fetch_rti_query_detail(rti_query_id: str = Path(..., description="The query ID")):
        # Mock logic: return 404 for "not_found" or if service returns None
        detail = QueryService.fetch_rti_query_detail(rti_query_id)
        if detail is None:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={
                    "data": None,
                    "message": f"RTI query {rti_query_id} not found",
                    "error": "RTI_QUERY_NOT_FOUND"
                }
            )
        return ApiResponse(
            data=detail,
            message="Query detail retrieved successfully",
            error=None
        )

    @staticmethod
    def assign_rti_query(rti_query_id: str = Path(..., description="The query ID")):
        # Mocking auth user as "current_authenticated_user"
        mock_user = "current_authenticated_user"

        # Mock: 404 if query_id is "not_found"
        if rti_query_id == "not_found":
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={
                    "data": None,
                    "message": f"RTI query {rti_query_id} not found",
                    "error": "RTI_QUERY_NOT_FOUND"
                }
            )

        # Mock: 409 Conflict if query_id is "already_assigned"
        if rti_query_id == "already_assigned":
            return JSONResponse(
                status_code=status.HTTP_409_CONFLICT,
                content={
                    "data": None,
                    "message": "RTI query has already been assigned",
                    "error": "RTI_QUERY_ALREADY_ASSIGNED"
                }
            )

        data = QueryService.assign_rti_query(rti_query_id, mock_user)
        return ApiResponse(
            data=data,
            message="RTI query assigned successfully",
            error=None
        )
