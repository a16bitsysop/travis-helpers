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
#apk update
#apk add --no-cache --virtual .aport-deps git wget alpine-sdk pax-utils atools git sudo
apk add --update-cache --virtual .aport-deps alpine-conf alpine-sdk sudo
apk upgrade -a
setup-apkcache /var/cache/apk

adduser -D ${NME} && addgroup ${NME} abuild && addgroup ${NME} tty

echo "Defaults  lecture=\"never\"" > /etc/sudoers.d/${NME}
echo "${NME} ALL=NOPASSWD : ALL" >> /etc/sudoers.d/${NME}

echo "Downloading aport files list..."
afiles=$(wget -qO- "https://git.alpinelinux.org/aports/tree/$tobuild" | \
grep 'ls-blob' | sed "s+blame+plain+" | sed -r "s+.*ls-blob.*href='(.*)'.*+\1+" | xargs)
echo "Extracted filenames: $afiles"

(
mkdir -p aport
cd aport || exit 1
for afile in $afiles
do
  echo "Downloading $afile"
  wget -q "https://git.alpinelinux.org$afile"
done

echo "Preparing to build $tobuild"
[ -f ../APKBUILD.patch ] && patch -p1 -i ../APKBUILD.patch
[ -f ../prebuild.sh ] && sh ../prebuild.sh
[ -d ../newfiles ] && cp ../newfiles/* .
)

mv aport /home/"$NME"/
chown -R "$NME":"$NME" /home/"$NME"/aport
echo "Building $tobuild"
su -c "echo Running as "$(whoami)"  && PATH=$PATH:/sbin && cd ~/aport && export CBUILD=$(uname -m) && echo Arch is: "$CBUILD" && abuild-keygen -a -i -n && abuild checksum && abuild -A && abuild -r" - ${NME}

echo "Copying Packages"
cp -a /home/"$NME"/packages .

apk del .aport-deps
