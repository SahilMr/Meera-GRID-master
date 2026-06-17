#!/usr/bin/env bash
set -euo pipefail

TOPIC_NAME="${KAFKA_TOPIC:-meera-new-requests}"
BOOTSTRAP_SERVER="${KAFKA_BOOTSTRAP_SERVER:-127.0.0.1:9092}"
RETENTION_MS="${KAFKA_RETENTION_MS:-60000}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

if docker ps --format '{{.Names}}' 2>/dev/null | grep -q '^meera-kafka$'; then
  echo "Creating topic via Confluent Docker Kafka..."
  docker exec meera-kafka kafka-topics \
    --bootstrap-server localhost:9092 \
    --create \
    --if-not-exists \
    --topic "${TOPIC_NAME}" \
    --partitions 1 \
    --replication-factor 1 \
    --config "retention.ms=${RETENTION_MS}"
elif [[ -x "${PROJECT_ROOT}/kafka_local/bin/kafka-topics.sh" ]]; then
  echo "Creating topic via local Kafka install..."
  "${PROJECT_ROOT}/kafka_local/bin/kafka-topics.sh" \
    --bootstrap-server "${BOOTSTRAP_SERVER}" \
    --create \
    --if-not-exists \
    --topic "${TOPIC_NAME}" \
    --partitions 1 \
    --replication-factor 1 \
    --config "retention.ms=${RETENTION_MS}"
else
  echo "No Kafka broker found. Start Confluent Kafka first:"
  echo "  docker compose up -d && ./scripts/create_topic.sh"
  echo "Or start local Kafka:"
  echo "  ./scripts/start_kafka_local.sh && ./scripts/create_topic.sh"
  exit 1
fi

echo "Topic '${TOPIC_NAME}' ready (retention.ms=${RETENTION_MS})."
