from typing import List, Optional
from src.schema.chat_schema import (
    UserQueryRequest, UserQueryResponseData,
    GetSuggestionRequest, GetSuggestionResponseData,
    GetSessionChatItem, GetSessionResponseData
)

class ChatService:
    @staticmethod
    def user_query(request: UserQueryRequest) -> List[UserQueryResponseData]:
        return [
            UserQueryResponseData(
                query_id="mock_query_uuid",
                asst_response="Mock response for user query.",
                source=["source_document_1.pdf"]
            )
        ]

    @staticmethod
    def get_suggestion(request: GetSuggestionRequest) -> List[GetSuggestionResponseData]:
        return [
            GetSuggestionResponseData(
                suggestion_id="mock_suggestion_uuid",
                asst_suggestion="Mock suggested resolution steps.",
                source=["source_guideline_2.pdf"]
            )
        ]

    @staticmethod
    def get_session(rti_query_id: str, user_id: str) -> Optional[GetSessionResponseData]:
        if rti_query_id == "trigger_failure":
            raise Exception("Simulated DB failure")
        if rti_query_id == "not_found":
            return None
            
        return GetSessionResponseData(
            rti_query_id=rti_query_id,
            asst_suggestion="Mock active assistant suggestion",
            chat=[
                GetSessionChatItem(
                    user_query="Initial citizen inquiry text?",
                    user_query_id="user_q_1",
                    source="system",
                    asst_response="Initial system response advice."
                )
            ]
        )
