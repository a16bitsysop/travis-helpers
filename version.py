#!/usr/bin/env python3
from argparse import ArgumentParser
from urllib import request
from json import loads
from docker import from_env

def getDockerTag( URI):
	DOCKURI = "https://registry.hub.docker.com/v1/repositories/"
	tags = request.urlopen(DOCKURI + URI + "/tags")

	raw_data = tags.read()
	json_data = loads(raw_data.decode('utf-8'))

	lines = []
	for line in json_data:
        	lines.append(line['name'])

	lines.sort(key=lambda x: x, reverse=True)
	if lines[0] == "latest":
		lines.pop(0)

	return lines[0]

def getAlpineVer( APK ):
	client = from_env()
	CMD = 'sh -c "apk update > /dev/null; apk info -s ' + APK + ';"'
	result = client.containers.run('alpine', CMD).decode('utf-8').strip(APK + '-').split(' ', 1)[0]
	return result

parser = ArgumentParser()
parser.add_argument('-a', '--alpine', type=str,\
help='get latest version of alpine package "ALPINE"')
parser.add_argument('-d', '--docker', type=str,\
help='get latest docker tag of docker image "DOCKER"')
#parser.add_argument('-f', '--force', action='store_true',\
#help='do not check if needs update')
args = parser.parse_args()

if args.alpine:
	print(getAlpineVer(args.alpine))

if args.docker:
	print(getDockerTag(args.docker))
