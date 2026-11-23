# Security Policy

## Supported Versions

Only the latest release receives security fixes.

| Version | Supported |
| ------- | --------- |
| latest  | ✅        |
| older   | ❌        |

## Scope

This repository is a hardened Python container template. Relevant vulnerabilities include:

- CVEs in Flask or its transitive dependencies
- Container security issues (e.g. privilege escalation, root execution)
- Supply chain issues in the CI/CD pipeline (workflow injection, unpinned actions)
- Secrets exposure in workflow logs or image layers

## Reporting a Vulnerability

Report privately via [GitHub Security Advisories](../../security/advisories/new). Do not open a public issue.

Include:
- A description of the vulnerability and its impact
- Steps to reproduce or proof-of-concept
- Affected versions

## Response Timeline

| Milestone | Target |
| --------- | ------ |
| Acknowledgement | 2 business days |
| Triage and severity assessment | 5 business days |
| Fix or mitigation | 30 days for critical/high, 90 days for medium/low |
| Public disclosure | Coordinated with reporter after fix ships |
