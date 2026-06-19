from typing import Optional
from datetime import datetime
from src.schema.inward_schema import (
    InwardCreateRequest, InwardCreateResponseData, InwardDetailData,
    OfficeNoteCreateRequest, OfficeNoteCreateResponseData, OfficeNoteDetailData
)

class InwardService:
    @staticmethod
    def create_inward(request: InwardCreateRequest) -> InwardCreateResponseData:
        # Mock inward_id generation
        return InwardCreateResponseData(inward_id="mock_inward_uuid")

    @staticmethod
    def fetch_inward_detail(inward_id: str) -> Optional[InwardDetailData]:
        # Return None to trigger 404 simulation, or return a mock detail object if desired
        return None

    @staticmethod
    def create_office_note(request: OfficeNoteCreateRequest) -> OfficeNoteCreateResponseData:
        return OfficeNoteCreateResponseData(office_note_id="mock_office_note_uuid")

    @staticmethod
    def fetch_office_note_detail(office_note_id: str) -> Optional[OfficeNoteDetailData]:
        # Return None to trigger 404 simulation
        return None
