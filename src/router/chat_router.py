from fastapi import APIRouter
from src.controller.chat_controller import ChatController

router = APIRouter(tags=["Chat"])

# POST user_query
router.add_api_route(
    "/user_query",
    ChatController.user_query,
    methods=["POST"],
    summary="Citizen/user-facing query to assistant"
)

# POST get_suggestion
router.add_api_route(
    "/get-suggestion",
    ChatController.get_suggestion,
    methods=["POST"],
    summary="Trigger suggestion request if no existing session"
)

# GET get_session
router.add_api_route(
    "/get-session",
    ChatController.get_session,
    methods=["GET"],
    summary="Fetch chat history and suggestion for a query"
)
