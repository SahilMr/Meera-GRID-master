from typing import Optional
from fastapi import Query, status
from fastapi.responses import JSONResponse

from src.schema.common_schema import ApiResponse
from src.schema.chat_schema import ChatSubmitRequest
from src.service.chat_service import ChatService

class ChatController:
    @staticmethod
    def submit_rti_query(request: ChatSubmitRequest):
        # Validation checks
        if not request.user_query.strip():
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "data": None,
                    "message": "user_query cannot be empty",
                    "error": "EMPTY_USER_QUERY"
                }
            )
        if not request.user_id.strip():
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "data": None,
                    "message": "user_id cannot be empty",
                    "error": "EMPTY_USER_ID"
                }
            )

        data = ChatService.submit_rti_query(request)
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "data": {
                    "rti_query_id": data.rti_query_id,
                    "inward_id": data.inward_id
                },
                "message": "RTI query and inward record created successfully",
                "error": None
            }
        )

    @staticmethod
    def fetch_faq(department: Optional[str] = Query(None, description="Filter FAQs by department")):
        data = ChatService.fetch_faqs(department)
        return ApiResponse(
            data=data,
            message="FAQs retrieved successfully",
            error=None
        )

    @staticmethod
    def search_similar_queries(
        rti_query: str = Query(..., description="Query text to find matches for"),
        department: Optional[str] = Query(None, description="Department filter"),
        user_id: Optional[str] = Query(None, description="User ID filter"),
        limit: int = Query(5, ge=1, le=20, description="Max matches to return")
    ):
        if not rti_query.strip():
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "data": [],
                    "message": "rti_query parameter cannot be empty",
                    "error": "EMPTY_RTI_QUERY"
                }
            )

        data = ChatService.search_similar_queries(
            rti_query=rti_query,
            department=department,
            user_id=user_id,
            limit=limit
        )
        return ApiResponse(
            data=data,
            message="Similar queries retrieved successfully",
            error=None
        )

    @staticmethod
    def suggest_faq_match(
        rti_query: str = Query(..., description="Draft query text to match"),
        department: Optional[str] = Query(None, description="Department filter"),
        limit: int = Query(3, ge=1, le=10, description="Max suggestions to return")
    ):
        if not rti_query.strip():
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "data": [],
                    "message": "rti_query parameter cannot be empty",
                    "error": "EMPTY_RTI_QUERY"
                }
            )

        data = ChatService.suggest_faq_matches(
            rti_query=rti_query,
            department=department,
            limit=limit
        )
        return ApiResponse(
            data=data,
            message="FAQ matches suggested successfully",
            error=None
        )
