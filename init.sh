#!/bin/bash
set -e
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${BASE_DIR}/.dev/bin/activate"
python3 "${BASE_DIR}/main.py"
