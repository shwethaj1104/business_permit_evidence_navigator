from fastapi.encoders import jsonable_encoder

from app.schemas.api import SourceResponse, SyncResponse, VersionResponse, VersionSummary


def response(schema, record):
    # Convert timestamps while filtering out persistence-only fields.
    return schema.model_validate(jsonable_encoder(record.model_dump()))


class KnowledgeController:
    """Translate sync and review results into stable HTTP response models."""

    def __init__(self, service):
        # Keep controller dependencies limited to the ingestion service.
        self.service = service

    def start(self, request):
        # Return an accepted durable job rather than waiting for website fetching.
        return response(SyncResponse, self.service.start(request))

    def jobs(self, profile_id):
        # Map bounded job history to API contracts.
        return [response(SyncResponse, row) for row in self.service.list_jobs(profile_id)]

    def job(self, job_id):
        # Expose status for UI polling.
        return response(SyncResponse, self.service.get_job(job_id))

    def sources(self, profile_id):
        # Expose source dates without performing a refresh.
        return [response(SourceResponse, row) for row in self.service.list_sources(profile_id)]

    def versions(self, profile_id):
        # Return version comparisons without embeddings or raw MongoDB fields.
        return [response(VersionSummary, row) for row in self.service.list_versions(profile_id)]

    def version(self, version_id):
        # Map one full source snapshot into its review response.
        return response(VersionResponse, self.service.get_version(version_id))

    def review(self, version_id, request):
        # Map an explicit approval/rejection to its resulting version state.
        return response(VersionResponse, self.service.review(version_id, request.action))
