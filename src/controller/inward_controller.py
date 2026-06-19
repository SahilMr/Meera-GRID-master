from fastapi import status
from fastapi.responses import JSONResponse

from src.schema.common_schema import ApiResponse
from src.schema.inward_schema import (
    InwardCreateRequest, OfficeNoteCreateRequest
)
from src.service.inward import InwardService

class InwardController:
    @staticmethod
    def create_inward(request: InwardCreateRequest):
        # Validation checks
        # case_access_level_id, privacy_level_id, inward_priority_id allowed lookup simulation: [1, 2, 3]
        allowed_lookup_ids = [1, 2, 3]
        if request.case_access_level_id not in allowed_lookup_ids:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "data": None,
                    "message": "Invalid case_access_level_id",
                    "error": "INVALID_CASE_ACCESS_LEVEL"
                }
            )
        if request.privacy_level_id not in allowed_lookup_ids:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "data": None,
                    "message": "Invalid privacy_level_id",
                    "error": "INVALID_PRIVACY_LEVEL"
                }
            )
        if request.inward_priority_id not in allowed_lookup_ids:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "data": None,
                    "message": "Invalid inward_priority_id",
                    "error": "INVALID_INWARD_PRIORITY"
                }
            )
        
        # Validate year: must be a reasonable year
        if request.year < 2000 or request.year > 2100:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "data": None,
                    "message": "Year must be between 2000 and 2100",
                    "error": "INVALID_YEAR"
                }
            )

        data = InwardService.create_inward(request)
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "data": {"inward_id": data.inward_id},
                "message": "Inward record created successfully",
                "error": None
            }
        )

    @staticmethod
    def fetch_inward_detail(inward_id: str):
        # Mock logic: return 404 if "not_found" or service returns None
        detail = InwardService.fetch_inward_detail(inward_id)
        if detail is None:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={
                    "data": None,
                    "message": f"Inward {inward_id} not found",
                    "error": "INWARD_NOT_FOUND"
                }
            )
        return ApiResponse(
            data=detail,
            message="Inward details retrieved successfully",
            error=None
        )

    @staticmethod
    def create_office_note(request: OfficeNoteCreateRequest):
        # Validation checks
        if not request.office_note.strip():
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "data": None,
                    "message": "office_note cannot be empty",
                    "error": "EMPTY_OFFICE_NOTE"
                }
            )

        # Mock check: if inward_id is "not_found", return 404
        if request.inward_id == "not_found":
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={
                    "data": None,
                    "message": "Linked inward record not found",
                    "error": "INWARD_NOT_FOUND"
                }
            )

        data = InwardService.create_office_note(request)
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "data": {"office_note_id": data.office_note_id},
                "message": "Office note created successfully",
                "error": None
            }
        )

    @staticmethod
    def fetch_office_note_detail(office_note_id: str):
        # Mock logic: return 404 if "not_found" or service returns None
        detail = InwardService.fetch_office_note_detail(office_note_id)
        if detail is None:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={
                    "data": None,
                    "message": f"Office note {office_note_id} not found",
                    "error": "OFFICE_NOTE_NOT_FOUND"
                }
            )
        return ApiResponse(
            data=detail,
            message="Office note details retrieved successfully",
            error=None
        )
