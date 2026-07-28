#!/bin/bash
# Daily driver for the morning news digest, called by cron.
#
# Cron runs with a minimal environment (no shell profile), so this script
# resolves its own paths and loads secrets from a local, gitignored .env file.
# It appends a timestamped record of each run to data/cron.log.

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR" || exit 1

# Load ANTHROPIC_API_KEY (and any overrides) from .env if present.
if [ -f .env ]; then
    set -a
    # shellcheck disable=SC1091
    . ./.env
    set +a
fi

mkdir -p data
{
    echo "===== digest run: $(date) ====="
    ./.venv/bin/python -m app.digest
    echo "===== exit code: $? ====="
    echo
} >> data/cron.log 2>&1
