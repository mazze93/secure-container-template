#!/usr/bin/env bash
set -euo pipefail

IMAGE="${IMAGE:-secure-container-template:dev}"
docker build -t "$IMAGE" .
echo "Built: $IMAGE"
