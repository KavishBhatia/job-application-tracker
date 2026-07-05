#!/bin/bash
set -e

PROJECT_DIR="/Users/kavishbhatia/hobby/job_application_tracker"
UV_BIN="/opt/homebrew/bin/uv"
HOST="127.0.0.1"
PORT="8000"
URL="http://${HOST}:${PORT}"
LOG_FILE="${PROJECT_DIR}/data/server.log"

cd "$PROJECT_DIR"
mkdir -p data

is_up() {
    curl -s -o /dev/null -m 1 "$URL"
}

if ! is_up; then
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
