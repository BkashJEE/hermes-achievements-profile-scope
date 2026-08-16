# Contributing to Hermes Achievements — Profile Scope Indicator

Thank you for improving this small patch package for [Hermes Agent](https://github.com/NousResearch/hermes-agent).

## Scope

This repository distributes only the profile-scope patch and its documentation. Contributions must stay limited to:

- `profile-scope.patch`;
- patch application and regression-test documentation;
- license, security, and contributor documentation.

Do **not** submit a full Hermes Agent checkout, user profiles, session databases, screenshots containing private data, local configuration, generated caches, credential files, or unrelated plugin work.

## Before opening a pull request

1. Fork this repository and create a focused branch.
2. Make the smallest change that solves one clear problem.
3. If you change `profile-scope.patch`, test it against the Hermes Agent base named in `README.md`:

   ```bash
   git apply --check /path/to/profile-scope.patch
   python -m pytest tests/plugins/test_achievements_plugin.py -q
   python -m unittest plugins/hermes-achievements/tests/test_achievement_engine.py -v
   python -m py_compile plugins/hermes-achievements/dashboard/plugin_api.py
   node --check plugins/hermes-achievements/dashboard/dist/index.js
   ```

4. Run `git diff --check`.
5. Review every changed and untracked file for secrets, personal data, local paths, profiles, session exports, `.env` files, keys, tokens, certificates, and generated artifacts.

## Contribution requirements

- Keep the patch backwards-compatible with persisted achievement snapshots where possible.
- Do not expose profile filesystem paths, session content, credentials, or private data in API responses or UI copy.
- Preserve keyboard access for interactive UI elements.
- Document the Hermes Agent revision used for patch compatibility when it changes.
- Write clear commit messages and complete the pull-request template.
- By submitting a contribution, you confirm that you have the right to submit it under this repository's MIT license.

## Review and merge policy

Maintainers triage pull requests as **ready for technical review**, **needs contributor changes**, or **blocked**. A clean test run does not authorize a merge. Every merge requires an accountable technical review, a documented security audit, and Dad's fresh approval for that exact GitHub action.

See [SECURITY.md](SECURITY.md) for vulnerability reporting.
