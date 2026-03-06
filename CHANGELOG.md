# Changelog

All notable changes to this project will be documented here.

## [Unreleased]
### Added
- Hadolint enforcement and SARIF upload in CI
- Trivy SARIF upload with policy baseline in `.trivy.yaml`
- Keyless cosign signing and verification for published GHCR image digests
- Dependabot patch/minor auto-approve and auto-merge workflow

### Changed
- Replaced Docker Scout/Docker Hub dependency with local Trivy policy checks
- Pinned all GitHub Actions in CI/release automation to full commit SHAs
- Refreshed README to document vendor-neutral hardening and supply-chain controls

## [0.1.0] - 2026-03-03
### Added
- Template repo structure (src/, tests/)
- Non-root Dockerfile baseline
- CI build with SBOM + provenance
- Docker Scout reporting + enforcement gates
- SemVer + release workflow
