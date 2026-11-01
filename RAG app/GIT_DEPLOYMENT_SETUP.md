# Branch and deployment setup

The local branch is `chore/azure-deployment-prep`. All application files were previously untracked; the first PR therefore introduces the application as well as deployment scaffolding. The existing root README is preserved.

## What runs on GitHub

- Pull requests to `main`: relevant frontend/backend checks. Backend CI builds the runtime Docker image and smoke-tests imports and the worker CLI without credentials or model calls.
- Pushes to `main`: checks and backend GHCR image publication using the commit SHA. Publishing does not create Azure resources. GitHub may create the package as private initially; review package visibility/access before configuring Azure image pulls.
- Azure deployment: only on main after checks, and only when repository variable `AZURE_DEPLOY_ENABLED` is exactly `true`. Leave it unset until all public-demo safeguards, cloud resources and secrets are ready.
- Deployments use a GitHub environment named `azure-demo`. Add required reviewers if available for your plan. Do not start an Azure deployment while a sync is active.

## GitHub configuration after the PR

1. In repository Settings → Environments, create `azure-demo`.
2. For GitHub-to-Azure login, create a federated identity trusting the subject `repo:shwethaj1104/business_permit_evidence_navigator:environment:azure-demo`. If the repository owner/name changes, adjust the subject. Configure appropriate deployment permissions scoped to the demo resources.
3. Add these variables in that environment:
   - `AZURE_CLIENT_ID`: CI/CD identity client ID, distinct from the API runtime identity.
   - `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID`.
   - `AZURE_RESOURCE_GROUP`, `AZURE_API_APP_NAME`, `AZURE_WORKER_JOB_NAME`.
   - `VITE_API_BASE_URL`: full API HTTPS URL ending in `/api/v1`.
4. Add environment secret `AZURE_STATIC_WEB_APPS_API_TOKEN` from the intended Static Web App.
5. Review GHCR package pull access for both the API and worker. The workflow publishes `ghcr.io/shwethaj1104/permit-navigator-backend:<sha>`.
6. Create/configure the resources using `DEPLOYMENT_CHECKLIST.md` and `AZURE_SYNC_SETUP.md`.
7. Configure API `CORS_ORIGINS` to the exact frontend origin. Keep credentials in Azure secret references. Do not put model keys in GitHub build variables or any `VITE_*` values.
8. Review public-demo protections before enabling deployment: owner-only knowledge updates, visitor chat isolation and usage limits are still outstanding. CORS does not provide authentication or prevent direct API calls.
9. Only when ready, set repository Actions variable `AZURE_DEPLOY_ENABLED=true`. Run both workflows manually on `main` or push matching changes. Repository-level placement is required because deployment gates are evaluated before environment jobs start.
10. Avoid letting the portal create a second workflow that deploys the same frontend.

## Local verification

From `RAG app/backend`:

```sh
uv sync --frozen --extra dev --extra azure
uv run --frozen --extra dev ruff check app scripts tests
uv run --frozen --extra dev ruff format --check app scripts tests
uv run --frozen --extra dev pytest -q
```

From `RAG app/frontend`:

```sh
npm ci
npm run lint
npm run format:check
npm run build
```

Docker is not available in the current development environment. CI will build and smoke-test the image; a successful local Python test suite is not a Docker validation result. No Azure deployment has been performed.

## Push and open the PR

After reviewing the staged source and confirming no secrets are present, commit if needed and push the feature branch:

```sh
git push -u origin chore/azure-deployment-prep
```

In GitHub choose **Compare & pull request**, base `main`, compare `chore/azure-deployment-prep`. Review CI results before merging. Do not enable Azure deployment just to merge this setup PR.
