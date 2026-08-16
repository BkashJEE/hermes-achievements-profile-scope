# Hermes Achievements — Profile Scope Indicator

An MIT-licensed Hermes Agent patch that tells you which profile produced the
**Unlocked** achievement total. It works with the default profile and every
valid named profile created by Hermes Agent.

## What it does

- Attributes achievement totals to the profile currently selected in Hermes.
- Adds a hoverable and keyboard-focusable info indicator beside **Unlocked**.
- Returns a display-safe `profile_scope` object from the achievements API.
- Never exposes the local Hermes filesystem path.
- Keeps older persisted snapshots compatible.

This feature keeps profiles separate. It does **not** combine every profile's
history into one total. Select a profile in the dashboard to see that profile's
result.

## Before you install

Install Hermes Agent first using its official installer. The patch was created
from Hermes commit `2be183142c6dd9ac309b6db5b783af5e25c3be18`, but the installer
checks the actual files instead of requiring that exact revision. Compatible
newer checkouts, including the current upstream `main`, are accepted; conflicting
or locally modified checkouts are refused instead of being forced.

The normal Hermes source locations are:

| Platform | Hermes source checkout |
| --- | --- |
| macOS | `~/.hermes/hermes-agent` |
| Windows | `%LOCALAPPDATA%\hermes\hermes-agent` |

## Install on macOS

```bash
git clone https://github.com/BkashJEE/hermes-achievements-profile-scope.git
cd hermes-achievements-profile-scope
bash install.sh
```

If Hermes is in a custom directory:

```bash
bash install.sh --hermes-dir /path/to/hermes-agent
```

## Install on Windows

Open PowerShell:

```powershell
git clone https://github.com/BkashJEE/hermes-achievements-profile-scope.git
cd hermes-achievements-profile-scope
powershell -ExecutionPolicy Bypass -File .\install.ps1
```

If Hermes is in a custom directory:

```powershell
powershell -ExecutionPolicy Bypass -File .\install.ps1 -HermesDir C:\path\to\hermes-agent
```

The installer shows the detected checkout and asks before changing it. It
creates a timestamped backup next to the Hermes checkout, applies the patch,
checks Python and JavaScript syntax, checks the installed markers, and prints
the exact next steps.

## Verify or uninstall

macOS:

```bash
bash install.sh --check
bash install.sh --uninstall
```

Windows:

```powershell
powershell -ExecutionPolicy Bypass -File .\install.ps1 -Check
powershell -ExecutionPolicy Bypass -File .\install.ps1 -Uninstall
```

Uninstall also creates a backup before reversing the patch. If patched files
have conflicting local changes, the installer stops instead of overwriting
them.

## Use any Hermes profile

Restart the dashboard after installation:

```bash
hermes dashboard
```

Then use the dashboard profile switcher, or launch with a named profile:

```bash
hermes -p <profile> dashboard
```

The implementation derives the selected profile from `HERMES_HOME`; it is not
hard-coded to any profile name, user, or machine path.

## Troubleshooting

- **Hermes checkout not found:** pass `--hermes-dir` / `-HermesDir` explicitly.
- **Checkout is incompatible:** update this project for your Hermes version;
  do not force the patch.
- **Patched files have local changes:** commit, stash, or restore those Hermes
  files first.
- **PowerShell blocks scripts:** use the documented `-ExecutionPolicy Bypass`
  command for this invocation after reviewing `install.ps1`.
- **Dashboard still shows the old UI:** stop the running dashboard and launch it
  again.

## Maintainer verification

The CI workflow installs, checks, tests, uninstalls, and requires an exact clean
rollback on macOS, Windows, and Linux against both the pinned patch base and
current upstream `main`. Local checks:

```bash
python -m unittest discover -s tests -v
python install.py --hermes-dir /path/to/hermes-agent --check
```

The patch was built against `NousResearch/hermes-agent` `main` at
`2be183142c6dd9ac309b6db5b783af5e25c3be18`.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for patch scope, validation, and pull-request requirements. Security reports are covered by [SECURITY.md](SECURITY.md).

## License

The patch changes files in Hermes Agent, which is MIT licensed. See
[LICENSE](LICENSE).
