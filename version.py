#!/usr/bin/env python3
from argparse import ArgumentParser
from urllib import request
from json import loads
from docker import from_env
from natsort import natsorted
from bs4 import BeautifulSoup

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
	etag = data.getheader('ETag').strip('"')
	return etag

def getFileHash( IMG ):
	result = catFile(IMG, '/etc/githash')

	return result

def getGitRelease( REPO ):
	data = request.urlopen('https://github.com/' + REPO + '/releases/latest')
	release = data.url.rsplit('/',1)[1]
	if release != "releases":
		return release

	for raw in data.readlines():
		line = raw.decode('utf-8')
		if "releases/tag" in line:
			release = line.rsplit('/',1)[1].split('"',1)[0]
			return release

	return 0

def getCargoRelease( NAME ):
	head = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
	req = request.Request('https://lib.rs/crates/' + NAME, None, headers=head)
	data = request.urlopen(req)
	soup = BeautifulSoup(data, 'html.parser')
	vers =  soup.find(id='versions').find(property='softwareVersion').get_text().strip()
	return vers

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
help='get latest github hash of file "GHASH"')
parser.add_argument('-r', '--release', type=str,\
help='get latest github release of "release" (USERNAME/REPO)')
parser.add_argument('-c', '--cargo', type=str,\
help='get latest cargo release of "CARGO"')

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

if args.release:
	print(getGitRelease(args.release))

if args.cargo:
	print(getCargoRelease(args.cargo))
