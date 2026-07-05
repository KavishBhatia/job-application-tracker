#!/bin/bash
set -e

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd -- "${SCRIPT_DIR}/.." && pwd)"

export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:$PATH"
UV_BIN="${UV_BIN:-uv}"
HOST="127.0.0.1"
PORT="8000"
URL="http://${HOST}:${PORT}"
LOG_FILE="${PROJECT_DIR}/data/server.log"

cd "$PROJECT_DIR" || { osascript -e "display alert \"Job Application Tracker failed to start\" message \"Project directory not found: ${PROJECT_DIR}\""; exit 1; }
mkdir -p data

is_up() {
    curl -s -o /dev/null -m 1 "$URL"
}

if ! is_up; then
    if ! command -v "$UV_BIN" >/dev/null 2>&1; then
        osascript -e "display alert \"Job Application Tracker failed to start\" message \"uv not found (tried '${UV_BIN}'). Install uv and/or adjust PATH/UV_BIN in scripts/start_app.sh.\""
        exit 1
    fi

    nohup "$UV_BIN" run uvicorn src.app:app --host "$HOST" --port "$PORT" > "$LOG_FILE" 2>&1 &
    disown

    for _ in $(seq 1 30); do
        if is_up; then
            break
        fi
        sleep 0.5
    done
fi

if is_up; then
    open "$URL"
else
    osascript -e "display alert \"Job Application Tracker failed to start\" message \"Check the log at ${LOG_FILE}\""
fi
