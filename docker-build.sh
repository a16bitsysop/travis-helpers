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
    NAME=$(head -1 README.md| cut -d' ' -f2)
    DESC=$(head -2 README.md | tail -n1)
  else
    echo "$INFO not found"
  fi

URL=$(git config --get remote.origin.url)
#GIT_COMMIT

docker buildx build \
  --label "org.label-schema.schema-version=1.0" \
  --label "org.label-schema.build-date=$(date -u +"%Y-%m-%d %H:%M:%S")" \
  --label "org.label-schema.version=$VER" \
  --label "org.label-schema.vcs-ref=$TRAVIS_COMMIT" \
  --label "org.label-schema.vcs-url=https://github.com/$TRAVIS_REPO_SLUG" \
  --label "org.label-schema.name=$NAME" \
  --label "org.label-schema.version=$VER" \
  --label "org.label-schema.description=$DESC" \
  --label "alpine-version=$ALP_VER" \
  --platform linux/amd64,linux/386,linux/ppc64le,linux/s390x,linux/arm64,linux/arm/v7 \
  -t "$IMAGE_NAME:$1" -t "$IMAGE_NAME" --push .

