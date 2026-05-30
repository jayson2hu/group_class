#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PID_FILE="${ROOT_DIR}/.local_pids"

if [[ -f "${PID_FILE}" ]]; then
  read -r FRONTEND_PID BACKEND_PID < "${PID_FILE}" || true
  for PID in "${FRONTEND_PID:-}" "${BACKEND_PID:-}"; do
    if [[ -n "${PID}" ]] && kill -0 "${PID}" >/dev/null 2>&1; then
      kill "${PID}" || true
      echo "Stopped PID ${PID}"
    fi
  done
  rm -f "${PID_FILE}"
else
  echo "PID file not found, attempting port-based stop."
  for PORT in 5173 18000; do
    if command -v lsof >/dev/null 2>&1; then
      PIDS="$(lsof -ti tcp:${PORT} || true)"
      if [[ -n "${PIDS}" ]]; then
        kill ${PIDS} || true
        echo "Stopped PID(s) ${PIDS} on port ${PORT}"
      fi
    fi
  done
fi
