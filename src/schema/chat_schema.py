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
