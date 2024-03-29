#!/bin/sh
# called with aport branch/name eg: main/zsh
NME="builder"

if [ -n "$1" ]
then
  tobuild="$1"
else
  >&2 echo "No aport specified, eg: $0 main/zsh"
  exit 2
fi

echo "Setting up build environment..."
apk add --update-cache --upgrade --virtual .aport-deps alpine-conf alpine-sdk sudo findutils
apk upgrade -a
setup-apkcache /var/cache/apk

adduser -D ${NME} && addgroup ${NME} abuild && addgroup ${NME} tty

echo "Defaults  lecture=\"never\"" > /etc/sudoers.d/${NME}
echo "${NME} ALL=NOPASSWD : ALL" >> /etc/sudoers.d/${NME}

pull-apk-source.sh "$tobuild"

(
cd aport || exit 1
echo "Preparing to build $tobuild"
[ -f ../APKBUILD.patch ] && patch -p1 -i ../APKBUILD.patch
[ -f ../prebuild.sh ] && sh ../prebuild.sh
[ -d ../newfiles ] && cp ../newfiles/* .
)

mv aport /home/"$NME"/
chown -R "$NME":"$NME" /home/"$NME"/aport
echo "Building $tobuild"
su -c "echo Running as ""$(whoami)""  && PATH=$PATH:/sbin && cd ~/aport && export CBUILD=$(uname -m) && echo Arch is: ""$CBUILD"" && abuild-keygen -a -i -n && abuild checksum && abuild -A && abuild -r" - ${NME}

#apk del .aport-deps

echo "Copying Packages"
cd /tmp || exit 1
cp -a /home/"$NME"/packages .
cd packages/"$NME" || exit 1
[ -d x86_64 ] && cp -a x86_64 x86
[ -d unknown ] && cp -a unknown armv7
[ -d unknown ] && cp -a unknown x86

find ./ -type d ! -path "./.*" ! -iname ".*" -execdir echo {} \; \
-execdir ls -lah {} \;
