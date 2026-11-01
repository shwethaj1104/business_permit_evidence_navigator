from fastapi import APIRouter

from app.schemas.api import ProfileResponse
from app.services.profile_service import ProfileService

router = APIRouter(prefix="/profiles", tags=["profiles"])


@router.get("", response_model=ProfileResponse)
def list_profiles():
    # Supply both tabs with the same supported profile even before DB setup.
    return ProfileResponse(profiles=ProfileService().list())
