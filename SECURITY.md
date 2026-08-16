# Security Policy

## Supported version

Security fixes are assessed against the current `main` branch of this patch package.

## Reporting a vulnerability

Do **not** include vulnerability details, credentials, session data, local paths, or exploit code in a public issue.

1. Use GitHub's **Security** tab and **Report a vulnerability** when private vulnerability reporting is available for this repository.
2. If private reporting is unavailable, open a minimal public issue titled `Security contact requested` without technical details. A maintainer will arrange a private channel.
3. Include the affected patch version or commit, affected Hermes Agent revision, impact, reproduction conditions, and any safe mitigation.

## Handling policy

- Reports are triaged privately where possible.
- Maintainers verify the issue, prepare a minimal fix, and run the repository security audit before any commit or push.
- Public disclosure timing is decided by the repository owner after a fix or mitigation is available.

This repository must never accept secrets, API keys, tokens, profile exports, session databases, or personal data in reports or pull requests.
