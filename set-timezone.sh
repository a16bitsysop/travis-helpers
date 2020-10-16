#!/bin/sh

red=$'\e[1;31m'
grn=$'\e[1;32m'
yel=$'\e[1;33m'
#blu=$'\e[1;34m'
#mag=$'\e[1;35m'
#cyn=$'\e[1;36m'
end=$'\e[0m'

printf "%b" "${grn}"
apk update
echo "\$TIMEZONE= $TIMEZONE"
echo

if [ -n "$TIMEZONE" ]
then
  echo "Waiting for DNS"
  ping -c1 -W60 google.com || ping -c1 -W60 www.google.com || ping -c1 -W60 google-public-dns-b.google.com
  apk add --no-cache tzdata
  if [ -f /usr/share/zoneinfo/"$TIMEZONE" ]
  then
    echo "Setting timezone to $TIMEZONE"
    cp /usr/share/zoneinfo/"$TIMEZONE" /etc/localtime
    echo "$TIMEZONE" > /etc/timezone
  else
    printf "%b\n" "${red} $TIMEZONE does not exist"
  fi
  apk del tzdata
fi
[ -n "$1" ] && NAME="$1" || NAME="container"
printf "%b\n" "${yel} Starting $NAME at $(date +'%x %X') ${end}"
