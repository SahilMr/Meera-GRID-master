from fastapi import APIRouter
from src.controller.master_controller import MasterController

router = APIRouter(tags=["Master"])

# POST upload_department_master
router.add_api_route(
    "/upload/department-mapping-master",
    MasterController.upload_department_master,
    methods=["POST"],
    summary="Upload Department Mapping Master File for Bulk Upload"
)

# GET get_department_master
router.add_api_route(
    "/department-mapping-master",
    MasterController.get_department_master,
    methods=["GET"],
    summary="Fetch department mapping master based on department"
)
