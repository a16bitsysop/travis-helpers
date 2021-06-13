#!/bin/sh
# called inside aport folder
NME="builder"

if [ ! -f APKBUILD ]
then
  >&2 echo "No APKBUILD file to build"
  exit 2
fi

echo "Setting up build environment..."
apk add --update-cache --upgrade --virtual .aport-deps alpine-conf alpine-sdk sudo findutils
apk upgrade -a
setup-apkcache /var/cache/apk

adduser -D ${NME} && addgroup ${NME} abuild && addgroup ${NME} tty

echo "Defaults  lecture=\"never\"" > /etc/sudoers.d/${NME}
echo "${NME} ALL=NOPASSWD : ALL" >> /etc/sudoers.d/${NME}

chown -R "$NME":"$NME" ./*
echo "Building ..."
echo "Arch is: $(uname -m)"
su -c "abuild-keygen -a -i -n && cd /tmp && abuild checksum && abuild -A && abuild -r" - ${NME}

#apk del .aport-deps

echo "Copying Packages"
cd /tmp || exit 1
mkdir -p packages/$(uname -m)
cp -a /home/"$NME"/packages/* packages/$(uname -m)

find ./ -type d ! -path "./.*" ! -iname ".*" -execdir echo {} \; \
-execdir ls -lah {} \;
