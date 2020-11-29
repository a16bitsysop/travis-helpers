#!/bin/sh
# called with aport branch/name eg: main/zsh
if [ -n "$1" ]
then
  tobuild="$1"
else
  >&2 echo "No aport specified, eg: $0 main/zsh"
  exit 2
fi

echo "Downloading aport files list..."
afiles=$(wget -qO- "https://git.alpinelinux.org/aports/tree/$tobuild" | \
grep 'ls-blob' | sed "s+blame+plain+" | sed -r "s+.*ls-blob.*href='(.*)'.*+\1+" | xargs)
echo "Extracted filenames: $afiles"

(
mkdir -p aport
cd aport || exit 1
for afile in $afiles
do
  sleep 6s
  echo "Downloading $afile"
  wget -q "https://git.alpinelinux.org$afile"
done
)
