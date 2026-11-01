from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.dependencies import knowledge_controller
from app.controllers.knowledge_controller import KnowledgeController
from app.schemas.api import (
    ReviewRequest,
    SourceResponse,
    SyncRequest,
    SyncResponse,
    VersionResponse,
    VersionSummary,
)

router = APIRouter(prefix="/knowledge", tags=["knowledge"])
Controller = Annotated[KnowledgeController, Depends(knowledge_controller)]


@router.post("/sync", response_model=SyncResponse, status_code=202)
def start_sync(request: SyncRequest, controller: Controller):
    # Enqueue a manual refresh without fetching on the request thread.
    return controller.start(request)


@router.get("/jobs", response_model=list[SyncResponse])
def list_jobs(profile_id: str, controller: Controller):
    # List recent jobs including any active job after a page reload.
    return controller.jobs(profile_id)


@router.get("/jobs/{job_id}", response_model=SyncResponse)
def get_job(job_id: str, controller: Controller):
    # Report persisted progress from the independent worker.
    return controller.job(job_id)


@router.get("/sources", response_model=list[SourceResponse])
def list_sources(profile_id: str, controller: Controller):
    # List source freshness without triggering web traffic.
    return controller.sources(profile_id)


@router.get("/versions", response_model=list[VersionSummary])
def list_versions(profile_id: str, controller: Controller):
    # Read lightweight version history for the selected scope.
    return controller.versions(profile_id)


@router.get("/versions/{version_id}", response_model=VersionResponse)
def get_version(version_id: str, controller: Controller):
    # Fetch full text only when a user opens a source comparison.
    return controller.version(version_id)


@router.post("/versions/{version_id}/review", response_model=VersionResponse)
def review_version(version_id: str, request: ReviewRequest, controller: Controller):
    # Publish or reject one explicitly reviewed source version.
    return controller.review(version_id, request)
