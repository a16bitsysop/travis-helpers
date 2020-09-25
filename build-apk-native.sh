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
apk add --no-cache --virtual .aport-deps git wget alpine-sdk pax-utils atools git sudo
adduser -D ${NME} && addgroup ${NME} abuild && addgroup ${NME} tty

echo "Defaults  lecture=\"never\"" > /etc/sudoers.d/${NME}
echo "${NME} ALL=NOPASSWD : ALL" >> /etc/sudoers.d/${NME}

echo "Downloading aport files list..."
afiles=$(wget -qO- "https://git.alpinelinux.org/aports/tree/$tobuild" | \
grep 'ls-blob' | sed "s+blame+plain+" | sed -r "s+.*ls-blob.*href='(.*)'.*+\1+" | xargs)
echo "Extracted filenames: $afiles"

mkdir -p aport
cd aport && rm *
for afile in $afiles
do
  echo "Downloading $afile"
  wget -q "https://git.alpinelinux.org$afile"
done

[ -f ../APKBUILD.patch ] && patch -p1 -i ../APKBUILD.patch
[ -f ../prebuild.sh ] && sh ../prebuild.sh
cp ../newfiles/* .

cd ..
mv aport /home/"$NME"/
chown -R "$NME":"$NME" /home/"$NME"/aport
su -c 'echo "Running as $(whoami)"  && cd && cd aport && abuild-keygen -a -i -n && abuild checksum && abuild -r' - ${NME}

echo "Copying Packages"
cp -a /home/"$NME"/packages .

apk del .aport-deps
