#!/bin/sh

# $1 = text to send
# $2 = port to send to
# $3 = expected response
# $4 = IP address or name to send to (127.0.0.1 if missing)

echo "$1" | nc "${4-127.0.0.1}" "$2" | grep -q "$3" || exit 1
