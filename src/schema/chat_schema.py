from typing import Optional
from pydantic import BaseModel

class ChatSubmitRequest(BaseModel):
    user_query: str
    user_id: str
    department_id: int

class ChatSubmitResponseData(BaseModel):
    rti_query_id: str
    inward_id: str

class FaqItem(BaseModel):
    faq_id: str
    question: str
    answer: str

class SimilarQueryItem(BaseModel):
    rti_query_id: str
    query_text: str
    resolution: Optional[str] = None
    department: str
    relevance_score: float

class FaqSuggestItem(BaseModel):
    faq_id: str
    question: str
    answer: str
    relevance_score: float
