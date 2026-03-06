# Changelog

All notable changes to this project will be documented here.

## [Unreleased]
### Changed
- Replaced Docker Scout/Docker Hub CI dependency with local Trivy enforcement
- Removed external scanner secret requirements from the security workflow docs

## [0.1.0] - 2026-03-03
### Added
- Template repo structure (src/, tests/)
- Non-root Dockerfile baseline
- CI build with SBOM + provenance
- Docker Scout reporting + enforcement gates
- SemVer + release workflow
