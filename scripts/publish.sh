#!/bin/bash
set -e

USER="rayhanadev"
IMAGE="find-my-api"
GIT_HASH=$(git rev-parse --short HEAD)

docker build \
  -t "${USER}/${IMAGE}:${GIT_HASH}" \
  -t "${USER}/${IMAGE}:latest" \
  .

docker push "${USER}/${IMAGE}:${GIT_HASH}"
docker push "${USER}/${IMAGE}:latest"

echo "Docker image ${USER}/${IMAGE}:${GIT_HASH} and ${USER}/${IMAGE}:latest pushed successfully."
