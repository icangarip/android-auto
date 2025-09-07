# Repository Guidelines

## Project Structure & Modules
- `tiktok_comptia_bot.py`: main automation entry; manages sessions, logging, and actions via ADB.
- `test_adb.py`, `test_uiautomator.py`: quick connectivity/UI‑dump checks.
- `find_coordinates.py`: helper to probe tap points.
- `open_tiktok_and_dump.py`, `tiktok_automation.py`, `tiktok_*`: supporting TikTok automation scripts.
- `sessions/`: per‑run artifacts (`logs/`, `screenshots/`, JSON reports).
- `install_adb.sh`: install or validate ADB (Linux or WSL Windows ADB path).

## Build, Test, and Run
- Install ADB: `bash install_adb.sh` (Ubuntu/Debian or WSL).
- Device check: `python3 test_adb.py` (lists devices, probes size/density, taps center).
- UI dump probe: `python3 test_uiautomator.py` (creates/parses `/sdcard/ui_dump.xml`).
- Run bot: `python3 tiktok_comptia_bot.py` (creates `sessions/<timestamp>/`).

Prereqs: enable Developer Options + USB debugging, authorize device, and ensure `adb devices` shows it.

## Coding Style & Naming
- Python, 4‑space indent, PEP 8 where reasonable.
- Names: modules/functions `snake_case`, classes `CamelCase`, constants `UPPER_SNAKE`.
- CLI behavior: scripts should print clear step logs and exit non‑zero on failure.
- Lint/format (optional): `ruff`/`black` are welcome; keep diffs minimal.

## Configuration & Security
- ADB path is currently hard‑coded in scripts. Prefer reading `ADB_PATH` env var with a sensible default (e.g., `/usr/bin/adb` or `/mnt/c/.../adb.exe`). Example: `os.getenv("ADB_PATH", default_path)`.
- Do not commit personal paths, device IDs, or sensitive dumps. Large artifacts belong under `sessions/` and should be pruned before commits.

## Testing Guidelines
- Manual/integration focus:
  - Connectivity: `python3 test_adb.py` should pass and show device.
  - UI inspect: `python3 test_uiautomator.py` prints counts and key elements.
- Add small, script‑level checks where feasible; keep side effects behind `if __name__ == "__main__"`.

## Commit & Pull Requests
- Commits: imperative mood, concise subject, context in body. Example: `fix(adb): make path configurable via ADB_PATH`.
- PRs: include purpose, steps to validate (device model + Android version), relevant logs (`sessions/.../logs/session.log`), and screenshots if behavior changes.
- Keep changes focused; avoid mixing refactors with behavior changes.

## Architecture Overview
- Interaction is via `subprocess` calls to ADB (tap, swipe, dump UI) with per‑session logging and reports. Prefer small, testable helpers and centralized ADB invocation.
