# Security Model

## Supported Versions
Security updates are provided for the latest version of this project.

## Reporting a Vulnerability
If you discover a security vulnerability, please report it privately via GitHub Security Advisories.

Do not open public issues for security vulnerabilities.

We will acknowledge your report and investigate as quickly as possible.

## Purpose
This repository is a hardened application template. Its security model is built around one rule:

- Unreviewed code may be validated.
- Only reviewed mainline code may be published as an official artifact.

That rule drives the CI structure, branch protection policy, image-signing flow, and automation boundaries.

## Trust Boundaries

There are two distinct trust zones in CI:

- `validate`
  - Runs on pull requests and pushes.
  - Builds the candidate image once.
  - Executes tests, Dockerfile policy checks, runtime checks, and vulnerability scanning.
  - Produces a validated image archive artifact.
  - Does not publish packages.
  - Does not sign artifacts.

- `publish`
  - Runs only on `push` to `main` or release tags.
  - Consumes the exact image archive produced by `validate`.
  - Publishes the validated artifact to GHCR.
  - Signs and verifies the published digest with keyless cosign.

This separation prevents pull requests from minting first-party published artifacts.

## Merge And Release Policy

### Merge blockers

Changes must not merge unless:

- Python tests pass.
- The Dockerfile declares a non-root `USER`.
- The built image runs as non-root.
- The container health endpoint returns `200` and `{"status":"ok"}`.
- Trivy finds no fixable `HIGH` or `CRITICAL` vulnerabilities under the current policy.

Branch protection should require the `validate` check, not the `publish` check.

### Release blockers

Releases must not publish unless:

- `validate` succeeded in the same workflow run.
- The published artifact is the same artifact that `validate` approved.
- Cosign signing succeeds.
- Cosign verification succeeds against the GitHub Actions OIDC identity.

## Supply-Chain Controls

### Pinned execution surfaces

The repository pins:

- GitHub Actions by full commit SHA.
- Docker base image by digest.
- Hadolint runtime image by digest.

The goal is deterministic execution, not just version labeling.

### Artifact promotion

The repository follows a build-once model:

- CI builds one Docker archive in `validate`.
- Scans and runtime checks run against that archive.
- `publish` promotes that exact archive.

This avoids a scan/build mismatch where one artifact is checked and a different artifact is shipped.

### Signing model

Published images are signed with keyless cosign:

- Identity provider: `https://token.actions.githubusercontent.com`
- Signing principal: the repository workflow identity
- Artifact identity: `ghcr.io/<owner>/<repo>@<digest>`

Verification is part of the publish workflow, not a separate manual step.

## Vulnerability Policy

Trivy is configured to:

- Scan OS and library vulnerabilities.
- Treat `HIGH` and `CRITICAL` findings as in-scope.
- Ignore unfixed vulnerabilities.

The policy is intentionally actionable. It is designed to block issues the team can remediate now, not to create constant red builds from upstream issues with no fix available.

If a vulnerability is flagged:

1. Prefer rotating to a patched base image digest.
2. Then prefer updating affected application dependencies.
3. Only change scanner policy with explicit rationale.

Do not bypass the policy by downgrading severity or widening ignores without documenting the reason.

## Automation Policy

Dependabot automation is deliberately narrow:

- Auto-approve/auto-merge only indirect `pip` patch and minor updates.
- Direct dependencies remain manual review.
- GitHub Actions updates remain manual review.
- Major version updates remain manual review.

This is a risk-reduction measure, not a convenience feature.

## What This Template Does Not Promise

This template improves the default security posture, but it does not guarantee:

- Absence of zero-days.
- Perfect dependency trust.
- Runtime sandboxing in downstream deployments.
- Secure secret handling for applications that add new integrations.

Downstream projects still need environment-specific hardening, access control, secret management, and incident response procedures.

## Review Checklist

When reviewing future changes to this template, ask:

- Does this change blur the boundary between validation and publishing?
- Does it introduce a new floating dependency in CI or Docker?
- Does it expand automation without narrowing risk?
- Does it weaken artifact identity or signing guarantees?
- Does it make failures less interpretable?

If the answer to any of those is yes, the design should be challenged before merge.
