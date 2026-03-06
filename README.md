# secure-container-template
![Language](https://img.shields.io/badge/Language-Python-blue)
![Container](https://img.shields.io/badge/Runtime-Non--Root-critical)
![CI](https://img.shields.io/badge/CI-GitHub%20Actions-success)
![Status](https://img.shields.io/badge/Status-Template-brightgreen)

![Secure Container Template Social Preview](.github/social-preview.png)

A hardened Python container baseline with CI-backed security gates, supply-chain attestations, and practical defaults for production-minded teams.

## At a glance
- Non-root runtime and health contract checks.
- SBOM + provenance in release workflow.
- Docker Scout reporting and policy enforcement.

## Quick links
- [Repository Layout](#repository-layout)
- [Local Development](#local-development)
- [CI and Security Gates](#ci-and-security-gates)

## GitHub social preview
Upload `.github/social-preview.png` in repository `Settings -> General -> Social preview` to use the branded card on link shares.

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

Run the service locally:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m src.main
```

The health endpoint is available at `http://127.0.0.1:8000/health`.

## Required GitHub Secrets

The `CI` workflow expects these repository secrets:

- `DOCKERHUB_USERNAME`
- `DOCKERHUB_TOKEN`

These are used by the Docker Scout stages in [.github/workflows/ci.yml](.github/workflows/ci.yml).

Set them with GitHub CLI:

```bash
gh secret set DOCKERHUB_USERNAME --repo mazze93/secure-container-template
gh secret set DOCKERHUB_TOKEN --repo mazze93/secure-container-template
```

If you want Dependabot PRs to exercise the same Scout gate, add matching Dependabot secrets in the GitHub UI:

- `Settings` -> `Secrets and variables` -> `Dependabot`
- Create `DOCKERHUB_USERNAME`
- Create `DOCKERHUB_TOKEN`

After secrets are configured, rerun any failed CI jobs from the Actions tab.

## CI and Security Gates

The main workflow in [.github/workflows/ci.yml](.github/workflows/ci.yml) enforces:

- Python tests must pass.
- The `Dockerfile` must declare a non-root `USER`.
- The built image must have a non-root `Config.User`.
- Images published from `main` include SBOM and provenance attestations.
- Docker Scout `quickview` reports on published images.
- Docker Scout `cves` fails the workflow when fixable `critical` or `high` vulnerabilities are present.

This means non-root execution and fixable high-severity vulnerabilities are treated as merge blockers, not advisory output.

## Branch Protection

`main` should require the `test_and_container` status check before merge. That job contains the Scout enforcement path, so requiring it turns the vulnerability gate into a repository policy.

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
