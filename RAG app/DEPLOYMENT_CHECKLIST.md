# Azure deployment checklist

Prepared: 1 November 2026. Target: public interview demo with Docker, GitHub Actions, Azure Static Web Apps, Azure Container Apps, and the existing MongoDB Atlas database.

## How to use this checklist

- `[x]` means implemented and locally verified. It does not mean deployed to Azure.
- `[ ]` means work remains.
- **Codex**: I can prepare or change project files, run local checks, and diagnose errors.
- **You**: you perform account sign-in, billing choices, resource creation, permissions, and secret entry in your own accounts.
- **Both**: I prepare the code or configuration; you supply non-secret resource details or complete the cloud action.

Do the phases in order. This file contains instructions only: creating it does not create cloud resources, push code, or change your credentials. Never paste credentials into chat.

## Architecture and cost expectations

| Component | Target | Cost approach |
|---|---|---|
| React | Azure Static Web Apps | Free plan |
| FastAPI | Azure Container Apps | Consumption, minimum replicas 0, maximum initially 1 |
| Sync worker | Manual Azure Container Apps Job | One execution per manual Sync request; no idle polling worker |
| Database, vectors, source snapshots | Existing MongoDB Atlas | Keep the existing free cluster within its limits |
| Backend Docker image | GitHub Container Registry (GHCR) | Prefer public image for a portfolio; verify current account allowances |
| CI/CD | GitHub Actions | Standard runners; keep within applicable allowances |
| Model, embeddings, optional discovery | Existing OpenAI API account | Usage remains separately billable |

Azure is **not guaranteed to be completely free**. Container Apps currently has monthly free grants of 180,000 vCPU-seconds, 360,000 GiB-seconds and 2 million requests per subscription. API and worker resource usage share subscription-level grants. Logs, bandwidth, registry choices and other resources may cost extra. Scale-to-zero can cause a slower first request.

Eligible new Azure accounts offer $200 credit for 30 days. Continuing afterward requires moving to pay-as-you-go; free allowances still apply, but excess usage can be billed. A budget alert does not stop spending. Do not enable an always-running API replica or worker expecting a permanent zero bill.

References: [Container Apps billing](https://learn.microsoft.com/en-us/azure/container-apps/billing), [Static Web Apps plans](https://learn.microsoft.com/en-us/azure/static-web-apps/plans), [Azure account terms](https://azure.microsoft.com/en-us/pricing/purchase-options/azure-account).

## 1. Confirm the repository layout — Both

- [ ] **You:** confirm the intended repository root is `business_permit_evidence_navigator`, with `RAG app` inside it.
- [ ] **Codex:** inspect the existing Git root and history before adding or changing Git configuration.

```text
business_permit_evidence_navigator/   ← repository root
├── .github/
│   └── workflows/                  ← workflows must be at this level
└── RAG app/
    ├── frontend/
    ├── backend/
    ├── .env                        ← local only, never commit
    ├── .env.example
    ├── .gitignore
    ├── AZURE_SYNC_SETUP.md
    └── DEPLOYMENT_CHECKLIST.md
```

1. Open a terminal in `business_permit_evidence_navigator`.
2. Run `git rev-parse --show-toplevel` and `git status --short`.
3. If the directory is not a repository, initialize Git there only after confirming no parent repository already owns it.
4. Keep the current folder names; CI paths containing `RAG app` must be quoted in shell commands.
5. Keep API and worker together in `backend`: they share services and will use the same Docker image.

**Done when:** the repository root and all build paths are unambiguous. No separate frontend/worker repositories are needed.

## 2. Check secrets and Git exclusions — Codex, then You

- [ ] **Codex:** verify `.env`, `.venv`, caches, `node_modules`, and build output are ignored.
- [ ] **Codex:** check tracked filenames and history for accidentally committed credentials without printing secret values.
- [ ] **You:** rotate any credential previously committed or exposed; removing a file from the latest commit does not remove it from history.
- [ ] **Codex:** keep `.env.example` free of real credentials and document deployment settings.

1. Check ignore behavior from the repository root with `git check-ignore 'RAG app/.env'`.
2. Check tracked env filenames with `git ls-files 'RAG app/.env' 'RAG app/.env.*'`.
3. Only the placeholder `.env.example` should be eligible for commit.
4. Review the staged diff before each initial push; never use a command that prints `.env` contents.
5. Store real cloud secrets in Azure, not GitHub source files, Docker build arguments, or frontend variables.

**Done when:** the reviewed commit contains no credentials or local dependency folders.

## 3. Prepare public-demo controls — Both

- [ ] **You:** choose whether visitors may create chats, and whether histories should be private per visitor or shared demo examples.
- [ ] **Codex:** implement the chosen chat isolation rules; currently the unauthenticated app can expose shared saved conversations and their modification endpoints.
- [ ] **Codex:** protect Sync and approve/reject operations with an owner-only mechanism suitable for this demo.
- [ ] **Codex:** add server-side chat/request limits and bounded input sizes; make limits effective across restarts/replicas where required.
- [ ] **You:** set an OpenAI usage budget/alerts and fund only the intended demo usage. Verify which controls are alerts versus enforced caps.

1. Allow visitors to use the checklist assistant under a limited usage policy.
2. Keep knowledge changes restricted to the owner; hiding a button is not endpoint protection.
3. Do not put an administrative secret in a `VITE_*` variable; frontend build values are public.
4. Check that a visitor cannot rename/delete another visitor's chats under the chosen design.
5. Test rejection responses before publishing the public link.

**Done when:** anonymous visitors cannot modify shared knowledge or trigger unlimited paid work.

## 4. Prepare production frontend/API configuration — Codex

- [ ] Add a build-time frontend API base URL, for example `VITE_API_BASE_URL=https://<api-host>/api/v1`.
- [ ] Keep `/api/v1` as the local-development default where appropriate.
- [ ] Add a backend allowed-origin setting and CORS middleware for the exact frontend HTTPS origin.
- [ ] Verify readiness/health responses identify configuration failures without exposing secrets.
- [ ] Check SPA fallback behavior and add Static Web Apps routing configuration if needed.

1. Replace the current hardcoded relative API URL with configurable production support.
2. Make cloud frontend requests go directly to the API's HTTPS host.
3. Do not rely on Vite's development proxy in production.
4. Use an exact frontend origin, including `https://`, in backend CORS.
5. Rebuild the frontend whenever its API URL changes; adding an environment variable after static assets were built does not rewrite them.

**Done when:** a production build can call a separately hosted API. The Free static site uses direct cross-origin calls, not a paid linked-backend feature.

## 5. Prepare and test Docker — Codex; You for Docker installation

- [ ] **You:** install/start Docker locally if unavailable and confirm its terms fit your usage.
- [ ] **Codex:** add `backend/Dockerfile` and a matching `.dockerignore`.
- [ ] **Codex:** include the Azure dependency extra in the runtime image (`.[azure]` or equivalent locked installation).
- [ ] **Codex:** use a supported Python version, install dependencies, run as a non-root user, and exclude secrets/caches/tests where appropriate.
- [ ] **Codex:** test image startup, health and worker CLI without triggering paid syncs.

1. Use `RAG app/backend` as Docker build context so the root `.env` is outside the context.
2. Build one image for both API and worker, targeting the Azure-supported architecture (initially `linux/amd64`). Mac ARM builds must not accidentally publish an incompatible image.
3. Default API command: `python -m uvicorn app.main:app --host 0.0.0.0 --port 8000`.
4. Worker execution overrides the command to `python -m app.workers.sync_worker --job-id <saved-id>`.
5. Inject configuration at runtime, never bake keys into the image.
6. Inspect image contents and verify it starts without a development server or `--reload`.

**Done when:** the same immutable image can serve the API or run a targeted worker.

## 6. On-demand worker implementation — Codex, implemented locally

- [x] Save a manual sync request in MongoDB before attempting Azure launch.
- [x] Add `SYNC_DISPATCH_MODE=azure` while keeping `local` as the default.
- [x] Use API managed identity to read and start the configured Azure job.
- [x] Preserve the deployed execution template and pass the exact MongoDB job ID.
- [x] Suppress racing launches; atomically claim the selected job and maintain its lease.
- [x] Exit the worker after one targeted job; retain local polling mode and optional `--once`.
- [x] Keep launch failures visible and provide an explicit retry action.
- [x] Test with mocked Azure responses and isolated MongoDB test doubles; 54 backend tests passed at implementation time.
- [ ] **Both:** verify the complete workflow on actual Azure resources after deployment.

Read [AZURE_SYNC_SETUP.md](AZURE_SYNC_SETUP.md) for permissions, timeout settings, reservation expiry and recovery limitations. This code is ready for cloud configuration; no Azure resources have been provisioned.

## 7. Create GitHub repository and publish reviewed code — You; Codex can prepare commits/workflows

- [ ] **You:** create the GitHub repository, select visibility and enable Actions.
- [ ] **Codex:** prepare reviewed source and deployment files.
- [ ] **You:** authenticate Git locally and push the reviewed branch.

1. Create one repository named `business_permit_evidence_navigator` (or your chosen name).
2. For an existing local project, avoid creating a second conflicting project tree from a template.
3. Add the repository remote and verify it points to your account.
4. Review staged filenames/diff and push the intended branch, such as `main`.
5. Confirm GitHub displays `RAG app/frontend` and `RAG app/backend`.
6. Remember that public source and public Docker images are visible to everyone; inspect both before publishing.

**Done when:** the clean code is on GitHub and its branch/repository names are known.

## 8. Create Azure account, resource group and cost alerts — You

- [ ] Sign in, select the intended subscription and review trial/paid terms.
- [ ] Create one resource group, for example `permit-navigator-demo`.
- [ ] Choose a supported region with Container Apps/Jobs availability and acceptable quotas.
- [ ] Configure a small monthly budget and email notifications in Cost Management.

1. Open the Azure portal and confirm the active subscription.
2. Check remaining trial credit and expiration if applicable.
3. Create the resource group; use it for this demo's resources so cleanup is straightforward.
4. Create budget alerts at thresholds appropriate to your chosen budget.
5. Review estimates before each resource creation; budget alerts do not enforce a spending cap.
6. Avoid dedicated workload profiles, paid gateways, NAT gateways, custom domains, or extra databases unless deliberately selected.

**Done when:** you know the subscription, resource group, region, credit expiry and cost controls.

## 9. Publish the Docker image to GHCR — Both

- [ ] **Codex:** prepare GitHub Actions image build/publish workflow.
- [ ] **You:** enable the repository/package permissions needed for publication.
- [ ] **You:** choose public or private image visibility and approve its implications.

1. Publish to `ghcr.io/<lowercase-owner>/permit-navigator-backend:<commit-sha>`.
2. Use GitHub's workflow token with minimal required permissions for publishing.
3. Tag each release by commit SHA rather than deploying a mutable `latest` tag.
4. For a public portfolio image, verify public visibility and test image pulls.
5. If keeping the image private, configure Azure registry access with appropriate package-read credentials stored as secrets; account for rotation.
6. Use the same release image for API and worker. No Azure Container Registry is required for this plan.

**Done when:** Azure can pull the reviewed image. [Container Apps with GitHub Actions/GHCR](https://learn.microsoft.com/en-us/azure/container-apps/github-actions).

## 10. Create the API Container App — You; Codex prepares exact settings/commands

- [ ] Create a Container Apps environment using Consumption, without a dedicated workload profile.
- [ ] Review logging destination/retention and possible ingestion charges.
- [ ] Create the API Container App from the GHCR image.
- [ ] Configure HTTPS ingress and runtime secrets.

1. Choose the resource group/environment and name the app, for example `permit-navigator-api`.
2. Configure GHCR access as required by the image visibility.
3. Start with 0.25 vCPU / 0.5 GiB if supported and sufficient; adjust based on measured startup/runtime memory rather than assuming this size is adequate.
4. Set external HTTP ingress, target port `8000`, and HTTPS-only access.
5. Set minimum replicas `0`, maximum replicas initially `1`.
6. Add the MongoDB/OpenAI configuration from phase 12. Keep Azure dispatch mode local until the worker resource and identity are ready, and do not test Sync yet.
7. Deploy and record the API HTTPS URL.
8. Verify readiness and check startup logs; a reachable HTTP process is not proof of a working Atlas connection.

**Done when:** the backend is healthy and reachable over HTTPS with secrets confined to the server.

## 11. Create the Manual worker job — You; Codex prepares exact settings/commands

- [ ] Create one Azure Container Apps Job in the same environment.
- [ ] Configure a single container using the same backend image SHA as the API.
- [ ] Select Manual trigger, parallelism 1 and completion count 1.
- [ ] Configure secret references, timeout, managed identity permissions and dispatch mode.

1. Name the resource, for example `permit-navigator-sync`.
2. Set Manual trigger, not Schedule. No polling worker deployment is needed in Azure.
3. Use startup command `python -m app.workers.sync_worker` and arguments `--once` as a safe default; the API overrides arguments with `--job-id <id>` for each execution.
4. Add the worker environment values/secrets from phase 12.
5. Start with a 3600-second replica timeout; adjust after measuring real ingestion. Initially use replica retry limit 0 with explicit UI retries; reassess interruption recovery later.
6. In the API app's Identity settings, enable system-assigned managed identity.
7. Grant that API identity `Microsoft.App/jobs/read` and `Microsoft.App/jobs/start/action`, scoped to this worker job via a custom Azure role. Role creation/assignment requires suitable account permissions. Start permission is sensitive because execution overrides can reference worker secrets.
8. Copy the worker job's Azure resource ID.
9. Set API `AZURE_SYNC_JOB_RESOURCE_ID` to that ID and `SYNC_DISPATCH_MODE=azure`.
10. Use `AZURE_CLIENT_ID` only if deliberately selecting a user-assigned API identity.
11. Deploy/restart the API revision after configuration changes.

**Done when:** the API can authenticate and start the intended job only. [Azure jobs and permissions](https://learn.microsoft.com/en-us/azure/container-apps/jobs).

## 12. Configure secrets, Atlas and readiness — Both

- [ ] **You:** enter real secrets directly into Azure and configure Atlas access.
- [ ] **Codex:** prepare environment mappings and diagnose sanitized readiness/errors.

| Setting | API | Worker | Storage |
|---|---|---|---|
| `OPENAI_API_KEY` | Yes | Yes | Azure secret reference |
| `MONGODB_URI` | Yes | Yes | Azure secret reference |
| `MONGODB_DB_NAME=permit_navigator` | Yes | Yes | Environment value |
| `OPENAI_MODEL` | Yes | Yes | Supported model ID; verify access before deploying |
| `OPENAI_EMBEDDING_MODEL=text-embedding-3-small` | Yes | Yes | Environment value |
| `OPENAI_SEARCH_MODEL` | Shared config | Yes | Search-capable supported model ID |
| `SYNC_DISPATCH_MODE=azure` | Yes | Not needed for processing; leave `local` | Environment value |
| `AZURE_SYNC_JOB_RESOURCE_ID` | Yes | No | Environment value |
| `AZURE_CLIENT_ID` | Only for user-assigned identity | Not needed for this design | Environment value |
| Exact allowed frontend origin | Yes, once implemented | No | Environment value |
| `LOG_LEVEL=INFO` | Yes | Yes | Environment value |

1. Use the existing `permit_navigator` database; do not create another database service in Azure.
2. Grant the database user only the required database permissions.
3. Allow the documented outbound IP addresses of the API and worker environment in Atlas; verify they remain valid for the chosen Azure setup. Do not assume your laptop's current-IP rule covers Azure.
4. Do not silently switch Atlas access to all IPs. If restricted stable egress requires paid networking, review that tradeoff before proceeding.
5. Confirm existing collections and vector/search indexes are ready; run the documented setup command from an authorized environment only if necessary.
6. Verify both workloads can reach MongoDB, OpenAI and the approved official-source hosts.
7. Keep all credentials out of frontend configuration and logs.

**Done when:** both deployed processes can access the same database and required providers.

## 13. Create the frontend Static Web App — You; Codex configures build paths

- [ ] Create Azure Static Web Apps on the **Free** plan.
- [ ] Connect the correct GitHub repository and branch.
- [ ] Configure Vite build paths and the API HTTPS URL.

1. Create the static app in the chosen resource group and select Free.
2. Connect GitHub and authorize the correct repository/branch.
3. Use app location `RAG app/frontend`, output location `dist`, and an empty API location. The app uses Vite, so do not use React's older `build` output directory.
4. Set build command `npm run build` if the generated workflow requires an explicit command.
5. In the build workflow, set the frontend API base URL to `https://<api-host>/api/v1` using the variable implemented in phase 4. A portal runtime variable alone does not update prebuilt browser files.
6. Review the generated workflow before merging it; avoid duplicate frontend deployment workflows.
7. Run the workflow and record the resulting `https://<site>.azurestaticapps.net` URL.
8. Add that exact origin to the API's CORS setting and deploy the API configuration change.
9. Verify frontend requests target the API host, not `/api/v1` on the static site.

**Done when:** the public static URL loads and successfully calls the HTTPS backend. No custom domain is necessary. [Static Web Apps quickstart](https://learn.microsoft.com/en-us/azure/static-web-apps/getting-started).

## 14. Configure CI/CD and release permissions — Both

- [ ] **Codex:** create workflows under the repository-root `.github/workflows/`.
- [ ] **Codex:** run frontend lint/build and backend lint/tests before deployment.
- [ ] **Codex:** publish SHA-tagged images and update API and worker together.
- [ ] **You:** configure Azure/GitHub trust, repository variables and deployment secrets.

1. Use frontend path filters for `RAG app/frontend/**` and backend filters for `RAG app/backend/**`; include workflow and relevant shared-configuration changes too.
2. Run frontend jobs from `RAG app/frontend` and backend jobs from `RAG app/backend`, quoting paths in shell commands.
3. Use the supported Node version and Python 3.12; install dependencies from lockfiles. Include the Azure extra in the deployed image.
4. Build/test pull requests without exposing deployment credentials to untrusted forks.
5. Configure GitHub-to-Azure OpenID Connect federation for the intended repository/branch or protected deployment environment. Use this identity for deployment, not the API's runtime identity.
6. Set the required Azure client, tenant and subscription identifiers as workflow configuration. Grant deployment permissions only to the intended resource group/resources.
7. Keep the Static Web Apps deployment token in a GitHub secret if the chosen action requires it.
8. Deploy only after checks pass. Update the worker's configured image and the API to the same SHA; avoid updating the worker during an active sync.
9. Configure workflow concurrency so two deployments cannot race.
10. Push a harmless change and verify the correct components redeploy.

**Done when:** a reviewed push triggers tests and a traceable deployment without manual password-based Azure login.

## 15. End-to-end public demo verification — Both

- [ ] **Codex:** prepare smoke checks and review sanitized logs.
- [ ] **You:** verify actual deployed behavior and authorize any test that makes paid model/search calls.

1. Open the frontend URL in an incognito browser and on a phone.
2. Verify the welcome, five profile choices, disabled-until-complete checklist button and mobile layout.
3. Generate one checklist using approved evidence and open its citations.
4. Verify chat persistence, rename/delete behavior and the chosen visitor isolation rules.
5. Verify unauthorized users cannot call knowledge administration endpoints.
6. As the owner, click Sync once and confirm `update_runs` is saved before worker execution begins.
7. Confirm exactly the selected job is claimed, source outcomes appear, and the worker execution stops afterward.
8. Verify syncing does not publish evidence automatically; review/approval remains required.
9. Confirm idle time creates no new sync execution. Check resource scaling after traffic stops.
10. Test retry handling with a controlled mocked failure where possible; do not revoke live credentials just to test errors.
11. Test the UI after the backend has scaled to zero and note its first-request delay for interviews.
12. Check Cost Analysis and model usage after testing; billing data may arrive with delay.

**Done when:** the public URL works without your laptop or a locally running worker.

## 16. Rollback, costs and cleanup — Both

- [ ] **Codex:** document the previous working SHA, backend revision and frontend deployment.
- [ ] **You:** review costs during the demo period and after any configuration change.
- [ ] **Both:** verify rollback restores compatible API and worker versions.

1. Keep the previous known-good image SHA and deployment identifiers.
2. For a backend rollback, restore both API and worker images; avoid changing an execution already in progress.
3. Restore/redeploy the compatible frontend build if API contracts changed.
4. Before an interview, open the site and run a small smoke check so cold-start behavior is understood.
5. When finished with the demo, delete only the intended demo Azure resources/resource group after reviewing its contents. Stopping traffic alone does not delete chargeable resources.
6. Review remaining GHCR images, GitHub artifacts, Azure resources and billing; revoke unused deployment credentials/trust where appropriate.
7. Keep or remove Atlas data separately according to your needs; deleting an Azure resource group does not delete Atlas or stop someone from using an exposed API key.

## Information to provide when we start implementation

Provide non-secret values only:

- GitHub repository URL, visibility and deployment branch.
- Confirmation of the repository root/folder structure.
- Azure subscription ID, tenant ID, resource group and chosen region once created.
- API app name/URL, worker job resource ID and static frontend URL as they become available.
- Decision on visitor chat privacy and owner-only administration.
- Whether Docker is installed and whether the Azure account is new or existing.

Do not provide MongoDB passwords, OpenAI keys, Azure access tokens or deployment tokens in chat. Enter them directly into the relevant secret settings.

**First action:** complete phases 1–2. Then I can prepare the remaining application configuration, Docker and workflow files before you create/deploy cloud resources.

## Branch preparation update — 1 November 2026

- [x] Confirm repository root is `business_permit_evidence_navigator` and create `chore/azure-deployment-prep`.
- [x] Add root Git exclusions and verify the local `.env` is ignored; candidate-file scan found only a known synthetic logging-test URI.
- [x] Add backend Dockerfile and allowlist-based Docker context exclusions; runtime includes the Azure extra and runs as a non-root user.
- [x] Add production frontend API URL support, example frontend configuration and backend exact-origin CORS with a regression test.
- [x] Add frontend and backend workflows at repository root: PR validation, immutable image publication on main, and opt-in Azure deployments.
- [x] Document environment variables, OIDC subject, Static Web Apps secret and public-image pull setup in `GIT_DEPLOYMENT_SETUP.md`.
- [x] Local checks: 55 backend tests, backend lint/format, frontend build/lint/format.
- [ ] Docker build/runtime validation: Docker is unavailable locally; backend CI contains the image build and smoke checks.
- [ ] Push branch and run GitHub CI; create PR to main.
- [ ] Public-demo endpoint protection, chat privacy/isolation and usage limits remain required before enabling Azure deployment.
- [ ] Create/configure Azure resources and verify a live deployment. Keep repository variable `AZURE_DEPLOY_ENABLED` unset until ready.
