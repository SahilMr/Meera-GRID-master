from fastapi import APIRouter
from src.controller.inward_controller import InwardController

router = APIRouter(tags=["Inwards & Office Notes"])

# POST create_inward
router.add_api_route(
    "/inwards",
    InwardController.create_inward,
    methods=["POST"],
    summary="Create a new inward record"
)

# GET fetch_inward_detail
router.add_api_route(
    "/inwards/{inward_id}",
    InwardController.fetch_inward_detail,
    methods=["GET"],
    summary="Fetch the full administrative record for an inward"
)

# POST create_office_note
router.add_api_route(
    "/office-notes",
    InwardController.create_office_note,
    methods=["POST"],
    summary="Create a new office note tied to an inward"
)

# GET fetch_office_note_detail
router.add_api_route(
    "/office-notes/{office_note_id}",
    InwardController.fetch_office_note_detail,
    methods=["GET"],
    summary="Fetch a single office note by its ID"
)
