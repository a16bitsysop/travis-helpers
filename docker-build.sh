#!/bin/sh

echo "Building docker image: $IMAGE_NAME"
echo "With tag: $1"
echo "Alpine version in image: $2"
echo "Main package Version: $3"
ALP_VER="$2"
VER="$3"

INFO=README.md
  if [ -f "$INFO" ]; then
    echo "Reading $INFO..."
    NAME=$(head -1 README.md) | cut -d' ' -f2
    DESC=$(head -2 README.md | tail -n1)
  else
    echo "$INFO not found"
  fi

URL=$(git config --get remote.origin.url)
#GIT_COMMIT

docker BUILDX build \
--build-arg ALP_VER="$ALP_VER" \
--build-arg VCS_URL="https://github.com/$TRAVIS_REPO_SLUG" \
--build-arg BUILD_DATE=$(date -u +"%Y-%m-%d %H:%M:%S") \
--build-arg NAME="$NAME" \
--build-arg DESC="$DESC" \
--build-arg VER="$VER" \
--platform linux/amd64,linux/386,linux/ppc64le,linux/s390x,linux/arm64,linux/arm/v7 \
-t "$IMAGE_NAME:$1" -t "$IMAGE_NAME" --push .

