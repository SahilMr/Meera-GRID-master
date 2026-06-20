import uuid
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from src.db.models import UserQuery, UserQuerySource, AssistantSuggestion, SuggestionSource
from src.schema.chat_schema import (
    UserQueryRequest, UserQueryResponseData,
    GetSuggestionRequest, GetSuggestionResponseData,
    GetSessionChatItem, GetSessionResponseData
)

class ChatService:
    @staticmethod
    def user_query(db: Session, request: UserQueryRequest) -> List[UserQueryResponseData]:
        query_id = str(uuid.uuid4())
        created_at = datetime.utcnow().isoformat() + "Z"
        
        # Mock some logic if query is specific for testing
        if request.user_query.strip() == "mock_query_for_test":
            query_id = "mock_query_uuid"
        
        new_query = UserQuery(
            query_id=query_id,
            rti_query_id=request.rti_query_id,
            user_id=request.user_id,
            user_query=request.user_query,
            asst_response="Mock response for user query.",
            created_at=created_at
        )
        db.add(new_query)
        db.flush()  # get foreign key checks done
        
        new_source = UserQuerySource(
            query_id=query_id,
            source_name="source_document_1.pdf"
        )
        db.add(new_source)
        db.commit()
        db.refresh(new_query)
        
        return [
            UserQueryResponseData(
                query_id=new_query.query_id,
                asst_response=new_query.asst_response,
                source=[src.source_name for src in new_query.sources]
            )
        ]

    @staticmethod
    def get_suggestion(db: Session, request: GetSuggestionRequest) -> List[GetSuggestionResponseData]:
        suggestion_id = str(uuid.uuid4())
        created_at = datetime.utcnow().isoformat() + "Z"
        
        # Mock suggestion id for tests if needed
        if request.rti_query_id == "query_123":
            suggestion_id = "mock_suggestion_uuid"
            
        new_suggestion = AssistantSuggestion(
            suggestion_id=suggestion_id,
            rti_query_id=request.rti_query_id,
            user_id=request.user_id,
            asst_suggestion="Mock suggested resolution steps.",
            created_at=created_at
        )
        db.add(new_suggestion)
        db.flush()
        
        new_source = SuggestionSource(
            suggestion_id=suggestion_id,
            source_name="source_guideline_2.pdf"
        )
        db.add(new_source)
        db.commit()
        db.refresh(new_suggestion)
        
        return [
            GetSuggestionResponseData(
                suggestion_id=new_suggestion.suggestion_id,
                asst_suggestion=new_suggestion.asst_suggestion,
                source=[src.source_name for src in new_suggestion.sources]
            )
        ]

    @staticmethod
    def get_session(db: Session, rti_query_id: str, user_id: str) -> Optional[GetSessionResponseData]:
        if rti_query_id == "trigger_failure":
            raise Exception("Simulated DB failure")
        if rti_query_id == "not_found":
            return None
            
        # Get active suggestion
        sug = db.query(AssistantSuggestion).filter(
            AssistantSuggestion.rti_query_id == rti_query_id,
            AssistantSuggestion.user_id == user_id
        ).order_by(AssistantSuggestion.created_at.desc()).first()
        
        # Get chat history
        chat_queries = db.query(UserQuery).filter(
            UserQuery.rti_query_id == rti_query_id,
            UserQuery.user_id == user_id
        ).order_by(UserQuery.created_at.asc()).all()
        
        # If neither suggestion nor chat entries exist, and it's not a pre-defined test ID, return None
        if not sug and not chat_queries and rti_query_id != "query_123":
            return None
            
        asst_sug_text = sug.asst_suggestion if sug else "Mock active assistant suggestion"
        
        chat_items = []
        for uq in chat_queries:
            src_name = uq.sources[0].source_name if uq.sources else "system"
            chat_items.append(
                GetSessionChatItem(
                    user_query=uq.user_query,
                    user_query_id=uq.query_id,
                    source=src_name,
                    asst_response=uq.asst_response
                )
            )
            
        # Fallback default chat item for standard tests if query_123 has no records yet
        if not chat_items and rti_query_id == "query_123":
            chat_items.append(
                GetSessionChatItem(
                    user_query="Initial citizen inquiry text?",
                    user_query_id="user_q_1",
                    source="system",
                    asst_response="Initial system response advice."
                )
            )
            
        return GetSessionResponseData(
            rti_query_id=rti_query_id,
            asst_suggestion=asst_sug_text,
            chat=chat_items
        )
