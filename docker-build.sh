#!/bin/sh

echo "Building docker image: $IMAGE_NAME"
echo "With tag: $1"

docker buildx build --platform linux/amd64,linux/386,linux/ppc64le,linux/s390x,linux/arm64,linux/arm/v7 -t "$IMAGE_NAME:$1" -t "$IMAGE_NAME" --push .
RET="$?"
docker logout
exit "$RET"
