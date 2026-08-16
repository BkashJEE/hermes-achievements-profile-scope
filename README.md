# Hermes Achievements — Profile Scope Indicator

A small, MIT-licensed patch for the [Hermes Agent](https://github.com/NousResearch/hermes-agent) achievements dashboard.

## Problem

Achievement totals are calculated from the selected Hermes profile's session history. Before this patch, the **Unlocked** total did not identify that source, so a user could mistake a named profile's score for the default profile's score.

## What this patch changes

- Adds a display-safe `profile_scope` object to `GET /api/plugins/hermes-achievements/achievements`.
- Adds a hoverable and keyboard-focusable ⓘ indicator beside **Unlocked**.
- Explains the profile whose history produced the count, without exposing a local filesystem path.
- Keeps existing persisted snapshots compatible by falling back to the current profile when the old snapshot has no scope metadata.

## Apply to Hermes Agent

```bash
git clone https://github.com/NousResearch/hermes-agent.git
cd hermes-agent
git apply /path/to/profile-scope.patch
```

Then restart `hermes dashboard` so it mounts the updated plugin API.

## Validation performed

```bash
python -m pytest tests/plugins/test_achievements_plugin.py -q
python -m unittest plugins/hermes-achievements/tests/test_achievement_engine.py -v
python -m py_compile plugins/hermes-achievements/dashboard/plugin_api.py
node --check plugins/hermes-achievements/dashboard/dist/index.js
git diff origin/main...HEAD --check
```

The patch was built against `NousResearch/hermes-agent` `main` at `2be183142c6dd9ac309b6db5b783af5e25c3be18`.

## License

The patch changes files in Hermes Agent, which is MIT licensed. See [LICENSE](LICENSE).
