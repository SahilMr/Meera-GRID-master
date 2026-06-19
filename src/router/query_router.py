from fastapi import APIRouter
from src.controller.query_controller import QueryController
from src.controller.chat_controller import ChatController

router = APIRouter(tags=["Queries"])

# GET fetch_rti_query
router.add_api_route(
    "/rti-queries",
    QueryController.fetch_rti_query,
    methods=["GET"],
    summary="Fetch RTI Query records (List or Single)"
)

# GET fetch_rti_query_count
router.add_api_route(
    "/rti-queries/count",
    QueryController.fetch_rti_query_count,
    methods=["GET"],
    summary="Fetch aggregate counts of RTI Queries"
)

# GET search_similar_queries
router.add_api_route(
    "/rti-queries/similar",
    ChatController.search_similar_queries,
    methods=["GET"],
    summary="Find previously submitted similar RTI queries"
)

# GET fetch_rti_query_detail
router.add_api_route(
    "/rti-queries/{rti_query_id}",
    QueryController.fetch_rti_query_detail,
    methods=["GET"],
    summary="Fetch full details of a single RTI Query"
)

# POST assign_rti_query
router.add_api_route(
    "/rti-queries/{rti_query_id}/assign",
    QueryController.assign_rti_query,
    methods=["POST"],
    summary="Assign an RTI Query to the authenticated caller"
)
