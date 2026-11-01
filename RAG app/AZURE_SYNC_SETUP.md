# On-demand Azure sync worker

The UI calls the same Sync endpoint. In Azure mode the API saves `update_runs` in MongoDB, reserves a launch, and starts a Manual Azure Container Apps Job. It passes `--job-id <saved-id>` to the worker. The worker claims only that job, renews its lease during processing, and exits after finishing. No worker runs while idle, and no scheduler is introduced.

## Local development

The default `SYNC_DISPATCH_MODE=local` preserves the existing separate polling worker. Your real `.env` has not been changed. To test a single queued job without Azure:

```sh
cd backend
source .venv/bin/activate
python -m app.workers.sync_worker --job-id YOUR_MONGODB_JOB_ID
```

Or use `--once` to claim at most one queued job and exit. Neither mode schedules new jobs. The regular command without arguments remains local polling mode.

## Azure configuration still required

1. Install the Azure dependency extra in the API image: `pip install '.[azure]'` from `backend`. The lockfile includes this extra.
2. Create a **Manual** Azure Container Apps Job with one worker container, the backend image, and the MongoDB/OpenAI configuration and secret references. Set parallelism and completion count to 1. Start with a 3600-second execution timeout; adjust after measuring ingestion. Use replica retry limit 0 initially; retry failed syncs explicitly in the UI. Per-source failures remain visible in MongoDB outcomes.
3. Enable a system-assigned managed identity on the API Container App. Grant it `Microsoft.App/jobs/read` and `Microsoft.App/jobs/start/action` scoped to this worker job through a custom Azure role. These permissions are sensitive because execution overrides can use the job's secrets; keep this identity private to the backend.
4. Set API environment variables:
   - `SYNC_DISPATCH_MODE=azure`
   - `AZURE_SYNC_JOB_RESOURCE_ID=/subscriptions/YOUR_SUBSCRIPTION/resourceGroups/YOUR_GROUP/providers/Microsoft.App/jobs/YOUR_JOB`
   - `AZURE_CLIENT_ID` only for a user-assigned API managed identity.
5. Deploy the updated API and worker image. Configure Atlas network access for both workloads. Do not run the polling worker alongside the Azure job.
6. Click Sync and inspect both MongoDB `update_runs` and Azure execution logs. Approving evidence remains a separate action.

The dispatcher reads the deployed job template before starting it, retaining images, resources, environment values, and secret references. It overrides only the worker command and arguments. No Azure password or token is placed in the frontend.

## Retry behavior and limits

- Racing clicks reuse the active MongoDB job. A two-minute launch reservation suppresses repeated starts; MongoDB's atomic worker claim prevents duplicate processing if Azure still receives duplicate executions.
- Azure launch failures return an actionable 503 while keeping the queued record. Click Sync again to retry dispatch. An accepted launch with no worker progress can be retried after the reservation expires.
- An interrupted running job can be dispatched again after its worker lease and launch reservation expire. The worker's existing three-attempt cap and source checkpoints still apply.
- There is no periodic recovery dispatcher: recovery requires another Sync click. Saving the MongoDB job and starting Azure are two separate operations, not an atomic transaction.
- Worker exceptions return a nonzero process exit code in one-shot mode. Source-level outcomes and publication readiness must still be checked in the app.
- The API waits only for Azure to accept the start request, never for ingestion to finish. Existing frontend polling shows the MongoDB progress.

No Azure resources have been created or live cloud executions tested by this change. Docker and CI/CD deployment are separate next steps. Before public deployment, protect sync/review endpoints and add usage limits.

References: [Jobs concepts and overrides](https://learn.microsoft.com/en-us/azure/container-apps/jobs), [Start REST API](https://learn.microsoft.com/en-us/rest/api/resource-manager/containerapps/jobs/start?view=rest-resource-manager-containerapps-2025-01-01).
