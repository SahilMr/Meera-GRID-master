from fastapi import APIRouter
from src.controller.chat_controller import ChatController

router = APIRouter(tags=["Chat & FAQ Deflection"])

# POST submit_rti_query
router.add_api_route(
    "/chat/submit",
    ChatController.submit_rti_query,
    methods=["POST"],
    summary="Citizen-facing intake for creating inward and RTI query"
)

# GET fetch_faq
router.add_api_route(
    "/faqs",
    ChatController.fetch_faq,
    methods=["GET"],
    summary="Fetch FAQs (optionally filtered by department)"
)

# GET suggest_faq_match
router.add_api_route(
    "/faqs/suggest",
    ChatController.suggest_faq_match,
    methods=["GET"],
    summary="Suggest existing FAQ entries matching citizen draft queries"
)
