#!/bin/sh

echo "Building docker test image for: $IMAGE_NAME"

echo "Needs updating to a new scanner"
#docker buildx build -t "test_image" --load .

#set MICROSCANNER_TOKEN environment variable
#scan.sh test_image

#exit 1
exit "$?"
