#!/usr/bin/env bash
set -euo pipefail

echo "Setting up {{ cookiecutter.agent_name }} development environment..."

if [[ -n "${CONDA_DEFAULT_ENV:-}" || -n "${CONDA_PREFIX:-}" ]]; then
  echo "[ERROR] Conda environment is active (${CONDA_DEFAULT_ENV:-$CONDA_PREFIX})."
  echo "        Deactivate conda before setup — this scaffold uses a project .venv only."
  echo "        Run: conda deactivate   (repeat until the prompt shows no conda env)"
  exit 1
fi

PYTHON=""
for candidate in python3.11 python3.12 python3.13; do
  if command -v "$candidate" >/dev/null 2>&1; then
    PYTHON="$candidate"
    break
  fi
done

if [[ -z "$PYTHON" ]]; then
  echo "[ERROR] Python 3.11+ is required (tried python3.11, python3.12, python3.13)."
  echo "        Install one of those interpreters and retry."
  exit 1
fi

PY_VERSION="$("$PYTHON" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
echo "[INFO] Using Python: $($PYTHON --version) ($PYTHON)"

if [ ! -x ".venv/bin/pip" ]; then
  rm -rf .venv
  "$PYTHON" -m venv .venv
fi

echo "[INFO] .venv Python: $(.venv/bin/python --version)"

unset VIRTUAL_ENV

.venv/bin/pip install --upgrade pip poetry
POETRY_VIRTUALENVS_IN_PROJECT=1 POETRY_VIRTUALENVS_CREATE=false \
  .venv/bin/poetry env use .venv/bin/python
POETRY_VIRTUALENVS_IN_PROJECT=1 POETRY_VIRTUALENVS_CREATE=false \
  .venv/bin/poetry install --with dev

POETRY_ENV="$(cd -P .venv && pwd -P)"
RESOLVED_ENV="$(cd -P "$(POETRY_VIRTUALENVS_IN_PROJECT=1 .venv/bin/poetry env info -p)" && pwd -P)"
if [[ "$RESOLVED_ENV" != "$POETRY_ENV" ]]; then
  echo "[ERROR] Poetry is not using project .venv."
  echo "        Expected: $POETRY_ENV"
  echo "        Got:      $RESOLVED_ENV"
  echo "        Deactivate conda, remove .venv, and run make setup again."
  exit 1
fi

for tool in black ruff pyright pytest; do
  if [ ! -x ".venv/bin/$tool" ]; then
    echo "[ERROR] Toolchain incomplete: .venv/bin/$tool is missing after poetry install"
    exit 1
  fi
done

if git rev-parse --git-dir >/dev/null 2>&1; then
  .venv/bin/pre-commit install
else
  echo "Note: skipped pre-commit install (not a git repository yet)"
fi

echo "Setup complete. Run: make check && make test"
