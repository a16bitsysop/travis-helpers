#!/bin/sh

red='\e[1;31m'
grn='\e[1;32m'
yel='\e[1;33m'
#blu='\e[1;34m'
#mag='\e[1;35m'
#cyn=$'\e[1;36m'
end='\e[0m'

printf "%b" "${grn}"
apk update
echo " \$TIMEZONE= $TIMEZONE"
echo

if [ -n "$TIMEZONE" ]
then
  if [ "$1" != "unbound" ]
  then
    echo " Waiting for DNS"
    ping -c1 -W60 google.com || ping -c1 -W60 www.google.com || ping -c1 -W60 google-public-dns-b.google.com
    apk add --no-cache tzdata
  fi
  if [ -f /usr/share/zoneinfo/"$TIMEZONE" ]
  then
    echo " Setting timezone to $TIMEZONE"
    cp /usr/share/zoneinfo/"$TIMEZONE" /etc/localtime
    echo "$TIMEZONE" > /etc/timezone
  else
    printf "%b\n" "${red} $TIMEZONE does not exist"
  fi
  [ "$1" != "unbound" ] && apk del tzdata
fi
printf "%b\n" "${yel} Starting ${1-container} at $(date +'%x %X') ${end}"
