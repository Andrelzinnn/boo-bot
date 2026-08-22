#!/bin/bash
set -e
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ -d "${BASE_DIR}/.dev" ]; then
    source "${BASE_DIR}/.dev/bin/activate"
elif [ -d "${BASE_DIR}/.venv" ]; then
    source "${BASE_DIR}/.venv/bin/activate"
else
  echo "Erro: Nenhum Ambiente virtual encontrado" >&2
  exit 1
fi

python3 "${BASE_DIR}/main.py"
