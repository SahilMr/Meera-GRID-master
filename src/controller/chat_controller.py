from fastapi import status, Query, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from src.schema.chat_schema import UserQueryRequest, GetSuggestionRequest
from src.service.chat_service import ChatService
from src.db.database import get_db

class ChatController:
    @staticmethod
    def user_query(request: UserQueryRequest, db: Session = Depends(get_db)):
        if not request.user_query.strip():
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "data": [],
                    "message": "user_query cannot be empty",
                    "error": "EMPTY_USER_QUERY"
                }
            )
        if not request.user_id.strip():
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "data": [],
                    "message": "user_id cannot be empty",
                    "error": "EMPTY_USER_ID"
                }
            )
        if not request.rti_query_id.strip():
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "data": [],
                    "message": "rti_query_id cannot be empty",
                    "error": "EMPTY_RTI_QUERY_ID"
                }
            )

        try:
            data = ChatService.user_query(db, request)
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "data": [item.model_dump() for item in data],
                    "message": "Query processed successfully",
                    "error": None
                }
            )
        except Exception as e:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "data": [],
                    "message": "Failed to process query",
                    "error": str(e)
                }
            )

    @staticmethod
    def get_suggestion(request: GetSuggestionRequest, db: Session = Depends(get_db)):
        if not request.rti_query_id.strip():
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "data": [],
                    "message": "rti_query_id cannot be empty",
                    "error": "EMPTY_RTI_QUERY_ID"
                }
            )
        if not request.user_id.strip():
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "data": [],
                    "message": "user_id cannot be empty",
                    "error": "EMPTY_USER_ID"
                }
            )

        try:
            data = ChatService.get_suggestion(db, request)
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "data": [item.model_dump() for item in data],
                    "message": "Suggestion retrieved successfully",
                    "error": None
                }
            )
        except Exception as e:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "data": [],
                    "message": "Failed to retrieve suggestion",
                    "error": str(e)
                }
            )

    @staticmethod
    def get_session(
        rti_query_id: str = Query(..., description="Filter based on rti_query_id"),
        user_id: str = Query(..., description="Filter based on user_id"),
        db: Session = Depends(get_db)
    ):
        if not rti_query_id.strip():
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "data": None,
                    "message": "rti_query_id query parameter cannot be empty",
                    "error": "EMPTY_RTI_QUERY_ID"
                }
            )
        if not user_id.strip():
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "data": None,
                    "message": "user_id query parameter cannot be empty",
                    "error": "EMPTY_USER_ID"
                }
            )

        try:
            data = ChatService.get_session(db, rti_query_id, user_id)
            if data is None:
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={
                        "data": None,
                        "message": "Session not found",
                        "error": None
                    }
                )
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "data": data.model_dump(),
                    "message": "Session retrieved successfully",
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
