#!/bin/bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
if [[ ! -x .venv-vision/bin/python ]]; then echo "Primero: bash install_env_linux.sh"; exit 1; fi
exec .venv-vision/bin/python -m vision.server "$@"
