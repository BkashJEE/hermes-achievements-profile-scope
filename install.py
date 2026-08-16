#!/usr/bin/env python3
"""Safe cross-platform installer for the Hermes profile-scope patch."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from collections.abc import Mapping
from typing import Sequence


PATCH_BASE = "2be183142c6dd9ac309b6db5b783af5e25c3be18"
PATCH_FILE = Path(__file__).resolve().with_name("profile-scope.patch")
TARGETS = (
    "plugins/hermes-achievements/README.md",
    "plugins/hermes-achievements/dashboard/dist/index.js",
    "plugins/hermes-achievements/dashboard/dist/style.css",
    "plugins/hermes-achievements/dashboard/plugin_api.py",
    "tests/plugins/test_achievements_plugin.py",
)


class InstallError(RuntimeError):
    """An expected, user-actionable installation failure."""


def normalized_patch_bytes(path: Path = PATCH_FILE) -> bytes:
    """Return a Git-compatible LF patch even after a Windows checkout."""
    raw = path.read_bytes()
    return raw.replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def run(
    command: Sequence[str],
    *,
    cwd: Path | None = None,
    input_bytes: bytes | None = None,
    check: bool = True,
) -> subprocess.CompletedProcess[bytes]:
    try:
        result = subprocess.run(
            list(command),
            cwd=cwd,
            input=input_bytes,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
    except FileNotFoundError as exc:
        raise InstallError(f"Required command not found: {command[0]}") from exc
    if check and result.returncode != 0:
        detail = result.stderr.decode(errors="replace").strip()
        raise InstallError(detail or f"Command failed: {' '.join(command)}")
    return result


def git(repo: Path, *args: str, input_bytes: bytes | None = None, check: bool = True):
    return run(("git", "-C", str(repo), *args), input_bytes=input_bytes, check=check)


def is_hermes_checkout(path: Path) -> bool:
    return (
        (path / ".git").exists()
        and (path / "plugins/hermes-achievements/dashboard/plugin_api.py").is_file()
        and (path / "tests/plugins/test_achievements_plugin.py").is_file()
    )


def candidate_checkouts(
    *,
    platform_name: str | None = None,
    home: Path | None = None,
    environment: Mapping[str, str] | None = None,
) -> list[Path]:
    platform_name = platform_name or os.name
    home = home or Path.home()
    if environment is None:
        environment = os.environ
    candidates: list[Path] = []
    env_root = environment.get("HERMES_AGENT_ROOT", "").strip()
    if env_root:
        candidates.append(Path(env_root).expanduser())
    candidates.append(Path.cwd())
    if platform_name == "nt":
        local_app_data = environment.get("LOCALAPPDATA", "").strip()
        if local_app_data:
            candidates.append(Path(local_app_data) / "hermes" / "hermes-agent")
    candidates.append(home / ".hermes" / "hermes-agent")
    candidates.append(Path(__file__).resolve().parent.parent / "hermes-agent")
    unique: list[Path] = []
    seen: set[str] = set()
    for candidate in candidates:
        key = os.path.normcase(str(candidate.resolve(strict=False)))
        if key not in seen:
            seen.add(key)
            unique.append(candidate)
    return unique


def resolve_checkout(explicit: str | None) -> Path:
    if explicit:
        path = Path(explicit).expanduser().resolve()
        if not is_hermes_checkout(path):
            raise InstallError(
                f"Not a compatible Hermes source checkout: {path}\n"
                "Pass the directory that contains the Hermes .git and plugins folders."
            )
        return path
    for candidate in candidate_checkouts():
        if is_hermes_checkout(candidate):
            return candidate.resolve()
    searched = "\n  - ".join(str(path) for path in candidate_checkouts())
    raise InstallError(
        "Could not find the Hermes Agent source checkout. Searched:\n"
        f"  - {searched}\n"
        "Run again with --hermes-dir /path/to/hermes-agent."
    )


def patch_check(repo: Path, *, reverse: bool = False) -> subprocess.CompletedProcess[bytes]:
    args = ["apply", "--check", "--whitespace=nowarn"]
    if reverse:
        args.append("--reverse")
    args.append("-")
    return git(repo, *args, input_bytes=normalized_patch_bytes(), check=False)


def current_revision(repo: Path) -> str:
    return git(repo, "rev-parse", "HEAD").stdout.decode().strip()


def overlapping_changes(repo: Path) -> list[str]:
    result = git(repo, "status", "--porcelain", "--", *TARGETS)
    return [line.decode(errors="replace") for line in result.stdout.splitlines()]


def installation_state(repo: Path) -> str:
    if patch_check(repo, reverse=True).returncode == 0:
        return "installed"
    if patch_check(repo).returncode == 0:
        return "compatible"
    return "incompatible"


def backup_root(repo: Path) -> Path:
    return repo.parent / "backups" / "hermes-achievements-profile-scope"


def create_backup(repo: Path, operation: str) -> Path:
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    destination = backup_root(repo) / f"{stamp}-{operation}"
    suffix = 1
    while destination.exists():
        destination = backup_root(repo) / f"{stamp}-{operation}-{suffix}"
        suffix += 1
    for relative in TARGETS:
        source = repo / relative
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    manifest = {
        "operation": operation,
        "created_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "hermes_checkout": str(repo),
        "hermes_revision": current_revision(repo),
        "patch_sha256": hashlib.sha256(normalized_patch_bytes()).hexdigest(),
        "files": list(TARGETS),
    }
    (destination / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    return destination


def restore_backup(repo: Path, backup: Path) -> None:
    for relative in TARGETS:
        shutil.copy2(backup / relative, repo / relative)


def validate_install(repo: Path) -> list[str]:
    failures: list[str] = []
    backend = repo / "plugins/hermes-achievements/dashboard/plugin_api.py"
    frontend = repo / "plugins/hermes-achievements/dashboard/dist/index.js"
    source = backend.read_bytes()
    try:
        compile(source, str(backend), "exec")
    except SyntaxError as exc:
        failures.append(f"Python syntax check failed: {exc}")
    text = source.decode("utf-8", errors="replace")
    for marker in ("def profile_scope()", 'payload["profile_scope"]'):
        if marker not in text:
            failures.append(f"Installed backend marker missing: {marker}")
    node = shutil.which("node")
    if node:
        result = run((node, "--check", str(frontend)), check=False)
        if result.returncode != 0:
            failures.append(result.stderr.decode(errors="replace").strip())
    diff_check = git(repo, "diff", "--check", "--", *TARGETS, check=False)
    if diff_check.returncode != 0:
        failures.append(diff_check.stdout.decode(errors="replace").strip())
    return [failure for failure in failures if failure]


def confirm(repo: Path, action: str, assume_yes: bool) -> None:
    if assume_yes:
        return
    if not sys.stdin.isatty():
        raise InstallError("Interactive confirmation is unavailable; pass --yes to continue.")
    answer = input(f"{action.capitalize()} in {repo}? [y/N] ").strip().lower()
    if answer not in {"y", "yes"}:
        raise InstallError("Cancelled; no files were changed.")


def install(repo: Path, assume_yes: bool) -> None:
    state = installation_state(repo)
    revision = current_revision(repo)
    print(f"Hermes checkout: {repo}")
    print(f"Hermes revision: {revision}")
    if state == "installed":
        failures = validate_install(repo)
        if failures:
            raise InstallError("Patch appears installed but validation failed:\n- " + "\n- ".join(failures))
        print("Already installed and validation passed.")
        return
    if state == "incompatible":
        conflicts = overlapping_changes(repo)
        detail = "\n".join(conflicts) if conflicts else "No overlapping local edits detected."
        raise InstallError(
            "This Hermes checkout is not compatible with the published patch.\n"
            f"Current revision: {revision}\nPatch base: {PATCH_BASE}\n{detail}\n"
            "Update this project for the newer Hermes version instead of forcing the patch."
        )
    conflicts = overlapping_changes(repo)
    if conflicts:
        raise InstallError(
            "Refusing to modify Hermes because patched files have local changes:\n"
            + "\n".join(conflicts)
        )
    confirm(repo, "install the profile-scope indicator", assume_yes)
    backup = create_backup(repo, "install")
    try:
        git(repo, "apply", "--whitespace=nowarn", "-", input_bytes=normalized_patch_bytes())
        failures = validate_install(repo)
        if failures:
            restore_backup(repo, backup)
            raise InstallError(
                "Validation failed; original files were restored:\n- "
                + "\n- ".join(failures)
            )
    except Exception:
        if installation_state(repo) != "compatible":
            restore_backup(repo, backup)
        raise
    print(f"Installed successfully. Backup: {backup}")
    print("Restart the dashboard, then select any Hermes profile to see its scoped total.")
    print("Default: hermes dashboard")
    print("Named profile: hermes -p <profile> dashboard")


def uninstall(repo: Path, assume_yes: bool) -> None:
    state = installation_state(repo)
    if state == "compatible":
        print("The profile-scope patch is not installed; nothing to remove.")
        return
    if state != "installed":
        raise InstallError(
            "Cannot safely uninstall because the patched files contain incompatible changes."
        )
    confirm(repo, "uninstall the profile-scope indicator", assume_yes)
    backup = create_backup(repo, "uninstall")
    try:
        git(
            repo,
            "apply",
            "--reverse",
            "--whitespace=nowarn",
            "-",
            input_bytes=normalized_patch_bytes(),
        )
    except Exception:
        restore_backup(repo, backup)
        raise
    print(f"Uninstalled successfully. Pre-uninstall backup: {backup}")


def check(repo: Path) -> int:
    state = installation_state(repo)
    print(f"Hermes checkout: {repo}")
    print(f"Hermes revision: {current_revision(repo)}")
    print(f"Profile-scope state: {state}")
    if state == "installed":
        failures = validate_install(repo)
        if failures:
            print("Validation failures:\n- " + "\n- ".join(failures), file=sys.stderr)
            return 1
        print("Validation: passed")
        return 0
    if state == "compatible":
        print("Ready to install.")
        return 0
    print(
        f"Not compatible. The published patch was created from Hermes {PATCH_BASE}.",
        file=sys.stderr,
    )
    return 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Install the Hermes achievements profile-scope indicator safely."
    )
    parser.add_argument(
        "--hermes-dir",
        help="Hermes Agent source checkout (auto-detected when omitted).",
    )
    action = parser.add_mutually_exclusive_group()
    action.add_argument("--check", action="store_true", help="Check compatibility only.")
    action.add_argument("--uninstall", action="store_true", help="Remove the patch safely.")
    parser.add_argument("--yes", action="store_true", help="Skip the confirmation prompt.")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        repo = resolve_checkout(args.hermes_dir)
        if args.check:
            return check(repo)
        if args.uninstall:
            uninstall(repo, args.yes)
        else:
            install(repo, args.yes)
        return 0
    except InstallError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
