import logging
import re

import httpx

from app.core.errors import AppError
from app.core.logging import logged_operation

logger = logging.getLogger(__name__)
API_VERSION = "2025-01-01"


class AzureJobDispatcher:
    """Start a single-job worker execution using the API's managed identity."""

    def __init__(self, settings, credential_factory=None, transport=None):
        # Keep cloud credentials lazy so local development needs no Azure dependencies.
        self.settings = settings
        self.credential_factory = credential_factory
        self.transport = transport

    @logged_operation("azure.start_sync_job")
    def start(self, job_id):
        # Preserve the complete deployed template when overriding the worker's job argument.
        resource = self.settings.azure_sync_job_resource_id.rstrip("/")
        if not re.fullmatch(
            r"/subscriptions/[^/]+/resourceGroups/[^/]+/providers/Microsoft.App/jobs/[^/]+", resource
        ):
            raise AppError("Set AZURE_SYNC_JOB_RESOURCE_ID to the Azure Container Apps Job resource ID.", 503)
        factory = self.credential_factory
        if factory is None:
            from azure.identity import ManagedIdentityCredential

            factory = ManagedIdentityCredential
        options = {"client_id": self.settings.azure_client_id} if self.settings.azure_client_id else {}
        with factory(**options) as credential:
            token = credential.get_token("https://management.azure.com/.default").token
            with httpx.Client(timeout=30, transport=self.transport) as client:
                url = f"https://management.azure.com{resource}"
                headers = {"Authorization": f"Bearer {token}"}
                params = {"api-version": API_VERSION}
                response = client.get(url, headers=headers, params=params)
                if response.status_code != 200:
                    raise AppError(f"Azure job configuration read failed (HTTP {response.status_code}).", 503)
                template = response.json()["properties"]["template"]
                containers = template.get("containers", [])
                if len(containers) != 1:
                    raise AppError("Configure the Azure sync job with exactly one worker container.", 503)
                containers[0]["command"] = ["python", "-m", "app.workers.sync_worker"]
                containers[0]["args"] = ["--job-id", job_id]
                response = client.post(f"{url}/start", headers=headers, params=params, json=template)
                if response.status_code not in (200, 202):
                    raise AppError(f"Azure worker launch failed (HTTP {response.status_code}).", 503)
        logger.info("event=azure_worker_launch_accepted job_id=%s", job_id)


def build_dispatcher(settings):
    # Select explicit cloud dispatch without changing the existing local worker mode.
    if settings.sync_dispatch_mode == "local":
        return None
    if settings.sync_dispatch_mode == "azure":
        return AzureJobDispatcher(settings)
    raise AppError("SYNC_DISPATCH_MODE must be local or azure.", 503)
