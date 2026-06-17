#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

if ! command -v java >/dev/null 2>&1; then
  if [[ -d "${HOME}/miniconda3/lib/jvm" ]]; then
    export JAVA_HOME="${HOME}/miniconda3/lib/jvm"
    export PATH="${JAVA_HOME}/bin:${PATH}"
  fi
fi
KAFKA_HOME="${PROJECT_ROOT}/kafka_local"
CONFIG="${PROJECT_ROOT}/kafka/config/kraft-server.properties"
PID_FILE="${PROJECT_ROOT}/kafka/data/kafka.pid"
LOG_FILE="${PROJECT_ROOT}/kafka/data/kafka.log"

mkdir -p "${PROJECT_ROOT}/kafka/data/logs"

if [[ ! -x "${KAFKA_HOME}/bin/kafka-server-start.sh" ]]; then
  echo "Local Kafka not found at ${KAFKA_HOME}."
  echo "Download it with:"
  echo "  curl -fsSL https://downloads.apache.org/kafka/3.9.2/kafka_2.13-3.9.2.tgz | tar -xz -C kafka_local --strip-components=1"
  exit 1
fi

if [[ -f "${PID_FILE}" ]] && kill -0 "$(cat "${PID_FILE}")" 2>/dev/null; then
  echo "Local Kafka already running (pid $(cat "${PID_FILE}"))."
  exit 0
fi

if [[ ! -f "${PROJECT_ROOT}/kafka/data/meta.properties" ]]; then
  CLUSTER_ID="$("${KAFKA_HOME}/bin/kafka-storage.sh" random-uuid)"
  "${KAFKA_HOME}/bin/kafka-storage.sh" format \
    -t "${CLUSTER_ID}" \
    -c "${CONFIG}" \
    --standalone
fi

nohup "${KAFKA_HOME}/bin/kafka-server-start.sh" "${CONFIG}" > "${LOG_FILE}" 2>&1 &
echo $! > "${PID_FILE}"

for _ in $(seq 1 30); do
  if "${KAFKA_HOME}/bin/kafka-broker-api-versions.sh" --bootstrap-server 127.0.0.1:9092 >/dev/null 2>&1; then
    echo "Local Kafka started on 127.0.0.1:9092 (pid $(cat "${PID_FILE}"))."
    exit 0
  fi
  sleep 1
done

echo "Kafka did not become ready in time. Check ${LOG_FILE}"
exit 1
