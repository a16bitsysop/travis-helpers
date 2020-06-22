#!/usr/bin/env python3
from argparse import ArgumentParser
from urllib import request
from json import loads
from docker import from_env
from natsort import natsorted

def catFile( IMG, FILE ):
	result = client.containers.run(IMG, 'cat ' + FILE).decode('utf-8').strip()
	return result

def getDockerTag( URI ):
	DOCKURI = 'https://registry.hub.docker.com/v1/repositories/'
	tags = request.urlopen(DOCKURI + URI + '/tags')

	raw_data = tags.read()
	json_data = loads(raw_data.decode('utf-8'))

	lines = []
	for line in json_data:
		ver = line['name']
		if ver != 'latest':
			lines.append(ver)

	lines = natsorted(lines)

	return lines[-1]

def getAlpineApk( APK ):
	CMD = 'sh -c "apk update > /dev/null; apk info -s ' + APK + ';"'
	IMG = 'alpine'
	if args.edge:
		IMG = IMG + ':edge'
	result = client.containers.run(IMG, CMD).decode('utf-8').strip(APK + '-').split(' ', 1)[0]
	return result

def getAlpineVer( IMG = 'alpine' ):
	if IMG == 'alpine' and args.edge:
		IMG = IMG + ':edge'
	result = catFile(IMG, '/etc/alpine-release')
	return result

def getGitHash( FILE ):
	data = request.urlopen('https://raw.githubusercontent.com/' + FILE)
	etag = data.getheader('ETag')
	return etag

def getFileHash( IMG ):
	result = catFile(IMG, '/etc/githash')
	return result

parser = ArgumentParser()
parser.add_argument('-a', '--alpine', type=str,\
help='get latest version of alpine package "ALPINE"')
parser.add_argument('-b', '--base', action='store_true',\
help='get alpine base image version')
parser.add_argument('-m', '--myalp', type=str,\
help='get version of alpine in image "MYALP"')
parser.add_argument('-e', '--edge', action='store_true',\
help='use alpine edge version for command')
parser.add_argument('-d', '--docker', type=str,\
help='get latest docker tag of docker image "DOCKER"')
parser.add_argument('-f', '--fhash', type=str,\
help='get git hash saved in docker image "FHASH"')
parser.add_argument('-g', '--ghash', type=str,\
help='get latest git hash of file "GHASH"')

args = parser.parse_args()
client = from_env()

if args.alpine:
	print(getAlpineApk(args.alpine))

if args.base:
	print(getAlpineVer())

if args.myalp:
	print(getAlpineVer(IMG = args.myalp))

if args.docker:
	print(getDockerTag(args.docker))

if args.fhash:
	print(getFileHash(args.fhash))

if args.ghash:
	print(getGitHash(args.ghash))

