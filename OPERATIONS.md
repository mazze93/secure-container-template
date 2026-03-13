# Operations Guide

## Purpose

This document explains how to operate and maintain the template safely after the initial bootstrap.

It is focused on recurring production tasks:

- rotating pinned digests
- responding to CI failures
- maintaining the release pipeline
- preserving the intended trust boundaries

## Routine Maintenance

### Rotate the Docker base image digest

When Trivy flags a fixable OS vulnerability in the base image:

1. Inspect the current upstream digest for the intended base tag.
2. Prefer a patched image line with minimal behavior drift.
3. Update the `FROM ...@sha256:...` line in [Dockerfile](/Users/daedalus/Code/secure-container-template/Dockerfile).
4. Rerun CI and confirm `validate` passes.

Do not switch tags casually. Preserve the semantic intent of the image family unless there is a security-driven reason to change it.

### Rotate pinned runtime tooling

For any non-`uses:` tool executed in CI:

- update the pinned digest or verified binary reference
- validate the command syntax still matches the new image/tool behavior
- confirm the associated scanner or linter still emits compatible output formats

This applies especially to:

- Hadolint image digests
- base image digests
- any future CLI binary checks added to CI

### Rotate GitHub Actions SHAs

When updating a workflow action:

1. Resolve the tag to a full commit SHA.
2. Update the workflow reference with the SHA.
3. Keep the human-readable version comment beside it.
4. Verify the repository’s action pinning policy still accepts the workflow.

Never replace a pinned SHA with a floating major tag.

## Responding To CI Failures

### If `validate` fails in tests

The failure is application or test logic, not release logic.

Action:

- fix the code or test
- do not weaken branch protection
- do not bypass with manual publishing

### If `validate` fails in Hadolint

The Dockerfile is violating declared container policy.

Action:

- fix the Dockerfile
- if the rule is genuinely inappropriate, document why before suppressing it

### If `validate` fails in Trivy

Treat this as a real security event until proven otherwise.

Action order:

1. Determine whether the finding is in the base image or application dependencies.
2. If base image: rotate the base digest.
3. If application dependency: update the dependency.
4. If there is no fix available: confirm the finding should be covered by `ignore-unfixed`, then inspect whether workflow inputs drifted from policy.

Do not silently change scanner thresholds to make CI green.

### If `publish` fails

Common classes:

- artifact download/load issue
- GHCR push issue
- cosign sign or verify issue

Response:

- do not rerun by manually rebuilding a new image outside the workflow
- preserve the build-once promotion model
- fix the workflow and rerun from the validated artifact path

## Publishing And Releases

### Official artifact sources

Official published artifacts must come only from:

- `push` to `main`
- `push` of release tags matching `v*.*.*`

If a workflow change would allow artifact publication from pull requests, treat that as a security regression.

### Release flow

The release process is:

1. update `VERSION`
2. update `CHANGELOG.md`
3. tag the release
4. push `main` and tags
5. allow CI/release automation to publish and sign the release

Do not create ad hoc “hotfix” publish paths outside the workflow without updating this document and `SECURITY.md`.

## Dependabot Operations

Dependabot automation is intentionally conservative.

Safe auto-merge scope:

- indirect `pip` dependencies
- semver patch and minor updates

Manual review required:

- direct dependencies
- major updates
- GitHub Actions updates

If you want to broaden automation later, do it explicitly and update both policy docs first.

## Branch Protection Operations

The required branch protection status check should track the current trust boundary.

Right now that is:

- `validate`

If workflow job names change, update branch protection immediately. A stale required check can deadlock the repo or create a false sense of enforcement.

## Incident Handling Heuristics

Use this quick classification when something breaks:

- Test failure: application defect or test defect
- Policy failure: intended security enforcement
- Integration failure: workflow logic bug
- Environment failure: network, registry, Docker daemon, or GitHub service issue

That distinction matters. The right response to a real vulnerability is different from the right response to an unavailable registry.

## Design Guardrails

Before merging changes to this template, verify:

- `validate` still has no publish/sign privileges
- `publish` still only runs on trusted refs
- the published image still originates from the validated artifact
- new automation is narrow and auditable
- new tools are pinned or checksum-verified
- docs still describe the actual live behavior

If any of those are false, the template is drifting away from its intended operating model.
