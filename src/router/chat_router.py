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

# POST generate_initial_suggestion
router.add_api_route(
    "/generate_initial_suggestion",
    ChatController.generate_initial_suggestion,
    methods=["POST"],
    summary="Generate initial suggestion for a query"
)

# POST retrieve_chat_context
router.add_api_route(
    "/retrieve_chat_context",
    ChatController.retrieve_chat_context,
    methods=["POST"],
    summary="Retrieve chat context and generate follow-up answer"
)

# POST mask_and_index_completed_rti
router.add_api_route(
    "/mask_and_index_completed_rti",
    ChatController.mask_and_index_completed_rti,
    methods=["POST"],
    summary="Mask PII, embed, and index completed RTI case"
)
