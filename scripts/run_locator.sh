#!/usr/bin/env bash
set -euo pipefail

# Lightweight runner for the locator bot.
# - Picks sensible defaults
# - Optionally detects Windows host IP for Appium
# - Accepts quick flags to avoid long env exports

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")"/.. && pwd)"
cd "$ROOT_DIR"

# Load .env if present
if [[ -f .env ]]; then
  # shellcheck disable=SC1091
  source .env
fi

MINS="${RUN_MINS:-2}"
PKG="${TIKTOK_PACKAGE:-}"
SERVER="${APPIUM_SERVER:-}"
FAST="0"

usage() {
  cat <<EOF
Usage: $0 [-m minutes] [-p package] [-s server] [--fast]
  -m  Minutes to run (default: 2)
  -p  TikTok package (default autodetect -> musically or trill)
  -s  Appium server URL (default autodetect -> http://<windows_ip>:4723)
  --fast  Enable FAST_MODE=1 (shorter watch/load intervals for smoke runs)

Examples:
  $0 -m 2 --fast
  $0 -s http://100.75.55.92:4723 -p com.zhiliaoapp.musically
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    -m) MINS="$2"; shift 2;;
    -p) PKG="$2"; shift 2;;
    -s) SERVER="$2"; shift 2;;
    --fast) FAST="1"; shift;;
    -h|--help) usage; exit 0;;
    *) echo "Unknown arg: $1"; usage; exit 1;;
  esac
done

# Detect Windows host IP for Appium if not set
if [[ -z "${SERVER}" ]]; then
  # WSL trick: use nameserver from resolv.conf
  WIN_IP=$(awk '/nameserver /{print $2; exit}' /etc/resolv.conf 2>/dev/null || true)
  if [[ -n "${WIN_IP:-}" ]]; then
    SERVER="http://${WIN_IP}:4723"
  else
    SERVER="http://127.0.0.1:4723"
  fi
fi

# Quick server reachability check
if command -v curl >/dev/null 2>&1; then
  if ! curl -sS "${SERVER}/status" >/dev/null; then
    echo "⚠️  Cannot reach Appium at ${SERVER}. Is it running? (appium -a 0.0.0.0 -p 4723)" >&2
  fi
fi

# Detect TikTok package if not set and adb exists
if [[ -z "${PKG}" ]] && command -v adb >/dev/null 2>&1; then
  if adb shell pm list packages 2>/dev/null | grep -qi "com.zhiliaoapp.musically"; then
    PKG="com.zhiliaoapp.musically"
  elif adb shell pm list packages 2>/dev/null | grep -qi "com.ss.android.ugc.trill"; then
    PKG="com.ss.android.ugc.trill"
  fi
fi

# Fallback default package
if [[ -z "${PKG}" ]]; then
  PKG="com.zhiliaoapp.musically"
fi

export APPIUM_SERVER="${SERVER}"
export TIKTOK_PACKAGE="${PKG}"
export RUN_MINS="${MINS}"

if [[ "${FAST}" == "1" ]]; then
  export FAST_MODE=1
  : ${WATCH_MIN_SECS:=1}
  : ${WATCH_MAX_SECS:=3}
  : ${LOAD_SECS:=0.5}
  export WATCH_MIN_SECS WATCH_MAX_SECS LOAD_SECS
fi

echo "🚀 Running locator bot"
echo "   Server : ${APPIUM_SERVER}"
echo "   Package: ${TIKTOK_PACKAGE}"
echo "   Minutes: ${RUN_MINS} (FAST_MODE=${FAST_MODE:-0})"

exec python3 tiktok_with_locator.py

