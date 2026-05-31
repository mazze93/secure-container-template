# secure-container-template

A minimal Python container template with a hardened default posture:

- Non-root container runtime, served by a production WSGI server (gunicorn)
- Container `HEALTHCHECK` against the app's `/health` endpoint
- GitHub Actions CI with all actions pinned to commit SHAs
- SBOM and provenance on published images
- Docker Scout vulnerability reporting (best-effort, non-blocking)
- SemVer tags, signed release images, and GitHub Releases
- Dependabot for Python, Docker base image, and Actions updates

## Repository Layout

```text
.
├── .github/
│   ├── dependabot.yml
│   └── workflows/
│       ├── ci.yml
│       └── release.yml
├── src/
├── tests/
├── CHANGELOG.md
├── Dockerfile
├── LICENSE
├── VERSION
├── build.sh
├── requirements-dev.txt
├── requirements.txt
└── test.sh
```

## Local Development

Run the test suite:

```bash
./test.sh
```

Build the container:

```bash
./build.sh
```

Run the service locally (Flask development server):

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m src.main
```

The health endpoint is available at `http://127.0.0.1:8000/health`.

The container image instead serves the app with **gunicorn** (a production WSGI
server), matching `CMD` in the [Dockerfile](Dockerfile). To exercise the image
the way CI and production do:

```bash
./build.sh
docker run --rm -p 8000:8000 secure-container-template:dev
curl -s http://127.0.0.1:8000/health   # {"status":"ok"}
```

The image declares a `HEALTHCHECK`, so `docker ps` reports container health.

## Optional GitHub Secrets

The Docker Scout stages in [.github/workflows/ci.yml](.github/workflows/ci.yml)
authenticate to Docker Hub using these repository secrets:

- `DOCKERHUB_USERNAME`
- `DOCKERHUB_TOKEN`

They are **optional**, and both must be set for Scout to run. If either is
missing, CI skips the Scout reporting steps and the rest of the pipeline
(tests, container build, push, non-root verification) still runs. Scout only
executes on pushes to `main`, never on pull requests, and is **best-effort**:
a missing or invalid Docker Hub credential logs a warning but never fails the
publish job.

Set them with GitHub CLI:

```bash
gh secret set DOCKERHUB_USERNAME --repo mazze93/secure-container-template
gh secret set DOCKERHUB_TOKEN --repo mazze93/secure-container-template
```

After secrets are configured, rerun any CI jobs on `main` from the Actions tab.

> **Note:** all actions in these workflows are pinned to full-length commit
> SHAs (with the version as a trailing comment). This is required by the
> repository's "Allow select actions" policy and is a supply-chain best
> practice. Dependabot keeps the pinned SHAs and comments up to date.

## CI and Security Gates

The main workflow in [.github/workflows/ci.yml](.github/workflows/ci.yml) enforces:

- Python tests must pass.
- The `Dockerfile` must declare a non-root `USER`.
- The built image must have a non-root `Config.User`.
- Images published from `main` include SBOM and provenance attestations.
- Docker Scout `quickview` and `cves` report on images published from `main`.

Non-root execution is a hard merge blocker. Docker Scout CVE findings are
reported for visibility but are **non-blocking** by default — to turn fixable
`critical`/`high` CVEs back into a merge gate, set `exit-code: true` on the
"Docker Scout CVEs" step in [.github/workflows/ci.yml](.github/workflows/ci.yml).

## Published Images

Two images are published by the workflows in this repository:

| Image | Registry | Published by | Tags |
| --- | --- | --- | --- |
| `ghcr.io/mazze93/secure-container-template` | GitHub Container Registry | [`ci.yml`](.github/workflows/ci.yml) on push to `main` | `latest`, `sha-<commit>`, branch name |
| `docker.io/mazze93/secure-container-base` | Docker Hub | [`release.yml`](.github/workflows/release.yml) on `v*.*.*` tags | `<version>`, `sha-<commit>` |

Both are built with **SBOM** and **provenance** attestations. The release
image is additionally **multi-arch** (`linux/amd64`, `linux/arm64`) and
**signed with cosign** (keyless / Sigstore).

Pull and run the latest CI image:

```bash
docker run --rm -p 8000:8000 ghcr.io/mazze93/secure-container-template:latest
```

Inspect the attestations on a published image:

```bash
docker buildx imagetools inspect ghcr.io/mazze93/secure-container-template:latest
```

Verify a release image signature:

```bash
cosign verify docker.io/mazze93/secure-container-base:<version> \
  --certificate-identity-regexp '^https://github.com/mazze93/secure-container-template/' \
  --certificate-oidc-issuer https://token.actions.githubusercontent.com
```

## Branch Protection

`main` should require the `test_and_container` status check before merge. That job runs the tests and the non-root image verification, so requiring it turns those checks into a repository policy.

Recommended settings for `main`:

- Require a pull request before merging
- Require at least 1 approval
- Require status checks to pass before merging
- Require branches to be up to date before merging
- Required check: `test_and_container`
- Require conversation resolution before merging
- Apply rules to administrators

Equivalent GitHub CLI call:

```bash
gh api \
  --method PUT \
  -H "Accept: application/vnd.github+json" \
  /repos/mazze93/secure-container-template/branches/main/protection \
  -F required_status_checks.strict=true \
  -F required_status_checks.contexts[]=test_and_container \
  -F enforce_admins=true \
  -F required_pull_request_reviews.dismiss_stale_reviews=true \
  -F required_pull_request_reviews.require_code_owner_reviews=false \
  -F required_pull_request_reviews.required_approving_review_count=1 \
  -F required_conversation_resolution=true \
  -F restrictions= \
  -F allow_force_pushes=false \
  -F allow_deletions=false \
  -F block_creations=false \
  -F required_linear_history=false \
  -F lock_branch=false \
  -F allow_fork_syncing=true
```

## Release Ritual

The repository follows SemVer. Releases are created from Git tags matching `v*.*.*`.

To ship a new release:

```bash
echo "0.1.1" > VERSION
```

Update [CHANGELOG.md](CHANGELOG.md), then:

```bash
git add VERSION CHANGELOG.md
git commit -m "release: v0.1.1"
git tag v0.1.1
git push origin main --tags
```

Pushing the tag triggers [.github/workflows/release.yml](.github/workflows/release.yml), which creates the GitHub Release.
