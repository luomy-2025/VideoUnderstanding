#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
CONFIG_FILE="${REPO_ROOT}/config/baseline/config.toml"
LOG_FILE="$(
    python -c \
        '
import sys
import tomllib
from pathlib import Path

config_file = Path(sys.argv[1]).resolve()
with config_file.open("rb") as file:
    config = tomllib.load(file)
log_file = Path(config["logging"]["log_file"]).expanduser()
if not log_file.is_absolute():
    log_file = (config_file.parent / log_file).resolve()
print(log_file)
' \
        "${CONFIG_FILE}"
)"

mkdir -p "$(dirname -- "${LOG_FILE}")"
cd "${REPO_ROOT}"

{
    printf '\n[%s] 开始运行 VideoVista-2 基线\n' "$(date '+%Y-%m-%d %H:%M:%S')"
    python -u baseline/baseline-videovista2.py \
        --config "${CONFIG_FILE}"
    printf '[%s] VideoVista-2 基线运行结束\n' "$(date '+%Y-%m-%d %H:%M:%S')"
} 2>&1 | tee -a "${LOG_FILE}"
