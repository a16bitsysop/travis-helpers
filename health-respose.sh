#!/bin/sh

# $1 = text to send
# $2 = IP address to name to send to
# $3 = port to send to
# $4 = expected response

echo "$1" | nc "$2" "$3" | grep -q "$4" || exit 1
