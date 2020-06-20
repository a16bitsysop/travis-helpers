#!/usr/bin/env python3
from argparse import ArgumentParser
from urllib import request
from json import loads
from docker import from_env
from natsort import natsorted

def getDockerTag( URI):
	DOCKURI = "https://registry.hub.docker.com/v1/repositories/"
	tags = request.urlopen(DOCKURI + URI + "/tags")

	raw_data = tags.read()
	json_data = loads(raw_data.decode('utf-8'))

	lines = []
	for line in json_data:
		ver = line['name']
		if ver != "latest":
			lines.append(ver)

	lines = natsorted(lines)

	return lines[-1]

def getAlpineApk( APK ):
	client = from_env()
	CMD = 'sh -c "apk update > /dev/null; apk info -s ' + APK + ';"'
	IMG = "alpine"
	if args.edge:
		IMG = IMG + ":edge"
	result = client.containers.run(IMG, CMD).decode('utf-8').strip(APK + '-').split(' ', 1)[0]
	return result

def getAlpineVer():
	client = from_env()
	CMD = 'cat /etc/alpine-release'
	IMG = "alpine"
	if args.edge:
		IMG = IMG + ":edge"
	result = client.containers.run(IMG, CMD).decode('utf-8').strip()
	return result

def getGitHash( FILE ):
	data = request.urlopen("https://raw.githubusercontent.com/" + FILE)
	etag = data.getheader('ETag')
	return etag

parser = ArgumentParser()
parser.add_argument('-a', '--alpine', type=str,\
help='get latest version of alpine package "ALPINE"')
parser.add_argument('-b', '--base', action='store_true',\
help='get alpine base image version')
parser.add_argument('-e', '--edge', action='store_true',\
help='use alpine edge version for command')
parser.add_argument('-d', '--docker', type=str,\
help='get latest docker tag of docker image "DOCKER"')
parser.add_argument('-g', '--ghash', type=str,\
help='get latest git hash of file "GHASH"')

args = parser.parse_args()

if args.alpine:
	print(getAlpineApk(args.alpine))

if args.docker:
	print(getDockerTag(args.docker))

if args.base:
	print(getAlpineVer())

if args.ghash:
	print(getGitHash(args.ghash))
