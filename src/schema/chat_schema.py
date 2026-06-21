from typing import List, Optional
from pydantic import BaseModel

# user_query API
class UserQueryRequest(BaseModel):
    user_query: str
    user_id: str
    rti_query_id: str

class UserQueryResponseData(BaseModel):
    query_id: str
    asst_response: str
    source: List[str]

# get_suggestion API
class GetSuggestionRequest(BaseModel):
    rti_query_id: str
    user_id: str

class GetSuggestionResponseData(BaseModel):
    suggestion_id: str
    asst_suggestion: str
    source: List[str]

# get_session API
class GetSessionChatItem(BaseModel):
    user_query: str
    user_query_id: str
    source: str
    asst_response: str

class GetSessionResponseData(BaseModel):
    rti_query_id: str
    asst_suggestion: str
    chat: List[GetSessionChatItem]

# generate_initial_suggestion API
class GenerateInitialSuggestionRequest(BaseModel):
    rti_query: str

class InitialSuggestionResults(BaseModel):
    suggestion: str

class GenerateInitialSuggestionResponseData(BaseModel):
    results: InitialSuggestionResults

class GenerateInitialSuggestionResponse(BaseModel):
    data: GenerateInitialSuggestionResponseData
    message: str
    error: Optional[str] = None

# retrieve_chat_context API
class RetrieveChatContextRequest(BaseModel):
    rti_query: str
    suggested_flow: str
    user_chat_query: str

class FaissRtiObject(BaseModel):
    rti_query: str
    office_note: str

class RefinedResultItem(BaseModel):
    score: float
    content: FaissRtiObject

class RetrieveChatContextResponseData(BaseModel):
    refined_results: List[RefinedResultItem]

class RetrieveChatContextResponse(BaseModel):
    data: RetrieveChatContextResponseData
    message: str
    error: Optional[str] = None

# mask_and_index_completed_rti API
class MaskAndIndexCompletedRtiRequest(BaseModel):
    inward_id: str
    rti_query: str
    office_note: str

class MaskAndIndexCompletedRtiResponse(BaseModel):
    message: str
    error: Optional[str] = None
