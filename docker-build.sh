#!/bin/sh

echo "Building docker image: $IMAGE_NAME"
echo "With tag: $1"

#docker build --build-arg VCS_REF=`git rev-parse --short HEAD` --build-arg BUILD_DATE=`date -u +"%Y-%m-%dT%H:%M:%SZ"` .
#BUILD_DATE
#ALP_VER
#PKG_VER
URL=$(git config --get remote.origin.url)
#GIT_COMMIT

docker buildx build --platform linux/amd64,linux/386,linux/ppc64le,linux/s390x,linux/arm64,linux/arm/v7 -t "$IMAGE_NAME:$1" -t "$IMAGE_NAME" --push .
RET="$?"
docker logout
exit "$RET"
