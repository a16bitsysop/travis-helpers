#!/bin/sh

echo "Building docker test image for: $IMAGE_NAME"

PLATFORMS="linux/386 linux/ppc64le linux/s390x linux/arm64 linux/arm/v7"

for PLAT in $PLATFORMS
do
  docker buildx build -t "test_image" --platform "$PLAT" --load .
done
