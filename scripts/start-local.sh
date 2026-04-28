#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FRONTEND_PORT="${FRONTEND_PORT:-5173}"
BACKEND_PORT="${BACKEND_PORT:-18000}"
PYTHON_BIN="${PYTHON_BIN:-python3}"
UV_BIN="${UV_BIN:-uv}"
PID_FILE="${ROOT_DIR}/.local_pids"

if ! command -v "${PYTHON_BIN}" >/dev/null 2>&1; then
  echo "Python not found: ${PYTHON_BIN}" >&2
  exit 1
fi

if ! command -v "${UV_BIN}" >/dev/null 2>&1; then
  if [[ -x "${HOME}/.local/bin/uv" ]]; then
    UV_BIN="${HOME}/.local/bin/uv"
  else
    echo "uv not found: ${UV_BIN}" >&2
    exit 1
  fi
fi

export PYTHONPATH="${ROOT_DIR}"
export GROUP_CLASS_BACKEND_HOST="0.0.0.0"
export GROUP_CLASS_BACKEND_PORT="${BACKEND_PORT}"

pushd "${ROOT_DIR}" >/dev/null
nohup "${UV_BIN}" run uvicorn apps.group_class_backend.app:app \
  --host "${GROUP_CLASS_BACKEND_HOST:-0.0.0.0}" \
  --port "${BACKEND_PORT}" >/tmp/group_class_backend.log 2>&1 &
BACKEND_PID=$!
popd >/dev/null

pushd "${ROOT_DIR}/apps/group_class_frontend" >/dev/null
nohup "${PYTHON_BIN}" -m http.server "${FRONTEND_PORT}" >/tmp/group_class_frontend.log 2>&1 &
FRONTEND_PID=$!
popd >/dev/null

echo "${FRONTEND_PID} ${BACKEND_PID}" > "${PID_FILE}"

sleep 1
echo "Frontend PID: ${FRONTEND_PID}"
echo "Backend PID : ${BACKEND_PID}"
echo "Frontend URL: http://127.0.0.1:${FRONTEND_PORT}/"
echo "Backend URL : http://127.0.0.1:${BACKEND_PORT}/"
echo
echo "If frontend should call backend:"
echo "localStorage.setItem('GROUP_CLASS_API_BASE_URL', 'http://127.0.0.1:${BACKEND_PORT}'); location.reload();"
