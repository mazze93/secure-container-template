# Changelog

All notable changes to this project will be documented here.

## [Unreleased]
### Fixed
- CI no longer fails at startup: every GitHub Actions action is now pinned to a
  full-length commit SHA, as required by the repository's allowed-actions
  policy. Previously `test_and_container` never ran.
- Pull requests (including Dependabot's) build and test without pushing, so they
  no longer fail on registry authentication.
- Docker Hub login and Docker Scout are best-effort and run after the image is
  pushed, so a missing/invalid Docker Hub credential can no longer block
  publishing.

### Changed
- Docker Scout CVE reporting is **non-blocking** by default (`exit-code: false`).
- Images are published to GHCR only on pushes to `main`.
- Container serves the app with gunicorn instead of the Flask development server.
- `release.yml` creates the GitHub Release via the `gh` CLI.
- Dropped the unused `pull-requests: write` permission from CI (least privilege).
- Added OCI image labels (title, description, licenses) to published images.

### Added
- Container `HEALTHCHECK` against the `/health` endpoint (stdlib-only).
- Dependabot coverage for the Docker base image.

### Removed
- `trivy.yml` workflow (disabled, redundant with Docker Scout, and not
  compatible with the allowed-actions policy).

## [0.1.0] - 2026-03-03
### Added
- Template repo structure (src/, tests/)
- Non-root Dockerfile baseline
- CI build with SBOM + provenance
- Docker Scout reporting + enforcement gates
- SemVer + release workflow
