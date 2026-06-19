from typing import List, Optional
from src.schema.chat_schema import (
    ChatSubmitRequest, ChatSubmitResponseData, FaqItem, SimilarQueryItem, FaqSuggestItem
)

class ChatService:
    @staticmethod
    def submit_rti_query(request: ChatSubmitRequest) -> ChatSubmitResponseData:
        return ChatSubmitResponseData(
            rti_query_id="mock_rti_query_uuid",
            inward_id="mock_inward_uuid"
        )

    @staticmethod
    def fetch_faqs(department: Optional[str] = None) -> List[FaqItem]:
        # Return empty list as requested
        return []

    @staticmethod
    def search_similar_queries(
        rti_query: str,
        department: Optional[str] = None,
        user_id: Optional[str] = None,
        limit: int = 5
    ) -> List[SimilarQueryItem]:
        # Return empty list as requested
        return []

    @staticmethod
    def suggest_faq_matches(
        rti_query: str,
        department: Optional[str] = None,
        limit: int = 3
    ) -> List[FaqSuggestItem]:
        # Return empty list as requested
        return []
