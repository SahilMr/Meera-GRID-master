from fastapi import status, Query, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from src.schema.chat_schema import (
    UserQueryRequest, GetSuggestionRequest,
    GenerateInitialSuggestionRequest, RetrieveChatContextRequest, MaskAndIndexCompletedRtiRequest
)
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

    @staticmethod
    def generate_initial_suggestion(request: GenerateInitialSuggestionRequest, db: Session = Depends(get_db)):
        if not request.rti_query.strip():
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "data": None,
                    "message": "rti_query cannot be empty",
                    "error": "EMPTY_RTI_QUERY"
                }
            )
        try:
            suggestion = ChatService.generate_initial_suggestion(db, request.rti_query)
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "data": {
                        "results": {
                            "suggestion": suggestion
                        }
                    },
                    "message": "Initial suggestion generated successfully",
                    "error": None
                }
            )
        except Exception as e:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "data": None,
                    "message": "Failed to generate initial suggestion",
                    "error": str(e)
                }
            )

    @staticmethod
    def retrieve_chat_context(request: RetrieveChatContextRequest, db: Session = Depends(get_db)):
        if not request.rti_query.strip():
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "data": None,
                    "message": "rti_query cannot be empty",
                    "error": "EMPTY_RTI_QUERY"
                }
            )
        if not request.suggested_flow.strip():
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "data": None,
                    "message": "suggested_flow cannot be empty",
                    "error": "EMPTY_SUGGESTED_FLOW"
                }
            )
        if not request.user_chat_query.strip():
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "data": None,
                    "message": "user_chat_query cannot be empty",
                    "error": "EMPTY_USER_CHAT_QUERY"
                }
            )
        try:
            refined_results, final_response = ChatService.retrieve_chat_context(
                db, request.rti_query, request.suggested_flow, request.user_chat_query
            )
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "data": {
                        "refined_results": refined_results
                    },
                    "message": final_response,
                    "error": None
                }
            )
        except Exception as e:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "data": None,
                    "message": "Failed to retrieve chat context",
                    "error": str(e)
                }
            )

    @staticmethod
    def mask_and_index_completed_rti(request: MaskAndIndexCompletedRtiRequest, db: Session = Depends(get_db)):
        if not request.inward_id.strip():
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "message": "inward_id cannot be empty",
                    "error": "EMPTY_INWARD_ID"
                }
            )
        if not request.rti_query.strip():
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "message": "rti_query cannot be empty",
                    "error": "EMPTY_RTI_QUERY"
                }
            )
        if not request.office_note.strip():
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "message": "office_note cannot be empty",
                    "error": "EMPTY_OFFICE_NOTE"
                }
            )
        try:
            ChatService.mask_and_index_completed_rti(
                db, request.inward_id, request.rti_query, request.office_note
            )
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "message": "PII masked and RTI index updated successfully",
                    "error": None
                }
            )
        except KeyError as e:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={
                    "message": "RTI query record not found with the provided inward ID",
                    "error": "RECORD_NOT_FOUND"
                }
            )
        except ValueError as e:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={
                    "message": "RTI query record is already closed",
                    "error": "ALREADY_CLOSED"
                }
            )
        except RuntimeError as e:
            return JSONResponse(
                status_code=522,
                content={
                    "message": "PII masking LLM failed or timed out",
                    "error": "LLM_ERROR"
                }
            )
        except Exception as e:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "message": "Failed to complete and archive RTI",
                    "error": str(e)
                }
            )
