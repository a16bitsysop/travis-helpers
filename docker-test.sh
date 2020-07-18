#!/bin/sh

echo "Building docker test image for: $IMAGE_NAME"

docker buildx build -t "test_image" --load .

#set MICROSCANNER_TOKEN environment variable
scan.sh test_image
