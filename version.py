#!/usr/bin/env python3
from argparse import ArgumentParser
from ftplib import FTP
from json import loads
from sys import exit
from urllib import error, request

from bs4 import BeautifulSoup
from docker import from_env
from natsort import natsorted


def catFile(IMG, FILE):
    try:
        res_ver = client.containers.run(IMG, "cat " + FILE).decode("utf-8").strip()
    except Exception as ex:
        ex = ex
        res_ver = "not.found"
    return res_ver


def getDockerTag(URI):
    DOCKURI = "https://registry.hub.docker.com/v1/repositories/"
    try:
        tags = request.urlopen(DOCKURI + URI + "/tags", timeout=timeo)
    except error.HTTPError as e:
        if hasattr(e, "reason"):
            exit("Failed to reach a server, does image exist: " + str(e.reason))
        elif hasattr(e, "code"):
            exit("The server could not fulfill the request: " + e.code)
        else:
            exit("unknown error")

    raw_data = tags.read()
    json_data = loads(raw_data.decode("utf-8"))

    lines = []
    for line in json_data:
        ver = line["name"]
        if ver != "latest" and ver != "docker-hub":
            lines.append(ver)

    return natsorted(lines)[-1]


def getAlpineApk(APK):
    CMD = 'sh -c "apk update > /dev/null; apk info -s ' + APK + ';"'
    IMG = "alpine"
    if args.edge:
        IMG = IMG + ":edge"
    result = (
        client.containers.run(IMG, CMD)
        .decode("utf-8")
        .strip(APK + "-")
        .split(" ", 1)[0]
    )
    return result


def getAlpineVer(IMG="alpine"):
    if IMG == "alpine" and args.edge:
        IMG = IMG + ":edge"
    return catFile(IMG, "/etc/alpine-release")


def getGitHash(FILE):
    data = request.urlopen("https://raw.githubusercontent.com/" + FILE, timeout=timeo)
    return data.getheader("ETag").strip('"')


def getFileHash(IMG):
    return catFile(IMG, "/etc/githash")


def getGitRelease(REPO):
    data = request.urlopen(
        "https://github.com/" + REPO + "/releases/latest", timeout=timeo
    )
    vers = data.url.rsplit("/", 1)[1]
    if vers == "releases":
        soup = BeautifulSoup(data, "html.parser")
        vers = soup.find("div", class_="commit").find("a").get_text().strip()
    if vers.startswith("v"):
        return vers[1:]
    return vers


def getGitlabRelease(REPO):
    requ = request.Request(REPO + "/-/tags/", None, headers=head)
    data = request.urlopen(requ, timeout=timeo)
    soup = BeautifulSoup(data, "html.parser")
    rawvers = soup.find_all(class_="item-title ref-name")
    allvers = []
    for i in rawvers:
        allvers.append(i.string)
    vers = natsorted(allvers)[-1]
    if vers.startswith("v"):
        return vers[1:]
    return vers

def getCargoRelease(NAME):
    requ = request.Request("https://lib.rs/crates/" + NAME, None, headers=head)
    data = request.urlopen(requ, timeout=timeo)
    soup = BeautifulSoup(data, "html.parser")
    vers = soup.find(id="versions").find(property="softwareVersion").get_text().strip()
    return vers


def getHTTPRelease(URI, NAME, EXT):
    ver_list = []
    requ = request.Request(URI, None, headers=head)
    try:
        data = request.urlopen(requ, timeout=timeo)
    except error.HTTPError as e:
        if hasattr(e, "reason"):
            exit("Failed to reach a server: " + str(e.reason))
        elif hasattr(e, "code"):
            exit("The server could not fulfill the request: " + e.code)
        else:
            exit("unknown error")
    except error.URLError as e:
        if hasattr(e, "reason"):
            exit("URL Error: " + str(e.reason))
        else:
            exit("unknown error")
    soup = BeautifulSoup(data, "html.parser")
    for link in soup.find_all("a"):
        filename = link.get("href").strip()
        if filename.startswith(NAME) and filename.endswith(EXT):
            ver = filename.replace(NAME, "").replace(EXT, "")
            if ver.startswith("-") or ver.startswith(".") or ver.startswith("v"):
                ver_list.append(ver[1:])
            else:
                ver_list.append(ver)
    if not ver_list:
        exit("No " + NAME + " found at " + URI)

    return natsorted(ver_list)[-1]


def getFTPRelease(URI, DIR, NAME, EXT):
    ftp_list = []

    def getname(recv_string):
        if recv_string.startswith(NAME) and recv_string.endswith(EXT):
            ver = recv_string.replace(NAME, "").replace(EXT, "")
            if ver.startswith("-") or ver.startswith(".") or ver.startswith("v"):
                ftp_list.append(ver[1:])
            else:
                ftp_list.append(ver)

    # open ftp connection
    ftp = FTP(URI)
    ftp.login()

    # list directory
    ftp.cwd(DIR)
    ftp.retrlines("NLST", callback=getname)
    ftp.quit()

    if not ftp_list:
        exit("No " + NAME + " found at " + URI)

    return natsorted(ftp_list)[-1]


parser = ArgumentParser()
parser.add_argument(
    "-a", "--alpine", type=str, help='get latest version of alpine package "ALPINE"'
)
parser.add_argument(
    "-b", "--base", action="store_true", help="get alpine base image version"
)
parser.add_argument(
    "-m", "--myalp", type=str, help='get version of alpine in image "MYALP"'
)
parser.add_argument(
    "-e", "--edge", action="store_true", help="use alpine edge version for command"
)
parser.add_argument(
    "-d", "--docker", type=str, help='get latest docker tag of docker image "DOCKER"'
)
parser.add_argument(
    "-f", "--fhash", type=str, help='get git hash saved in docker image "FHASH"'
)
parser.add_argument(
    "-g", "--ghash", type=str, help='get latest github hash of file "GHASH"'
)
parser.add_argument(
    "-r",
    "--release",
    type=str,
    help='get latest github release of "release(USERNAME/REPO)"',
)
parser.add_argument(
    "-s",
    "--gitlab",
    type=str,
    help='get latest gitlab tag from repo url "gitlab(USERNAME/REPO)"',
)
parser.add_argument(
    "-c", "--cargo", type=str, help='get latest cargo release of "CARGO"'
)
parser.add_argument(
    "-l",
    "--list",
    type=str,
    help='get latest http directory/webpage release of "LIST(package name),\
URL(full url),EXT(file extension eg tar.gz)"',
)
parser.add_argument(
    "-t",
    "--ftp",
    type=str,
    help='get latest ftp directory release of "FTP(package name),\
URL(ftp server),DIR(ftp directory),EXT(file extension eg tar.gz)"',
)

args = parser.parse_args()
client = from_env()
head = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) \
AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36"
}
timeo = 30

if args.alpine:
    print(getAlpineApk(args.alpine))

if args.base:
    print(getAlpineVer())

if args.myalp:
    print(getAlpineVer(IMG=args.myalp))

if args.docker:
    print(getDockerTag(args.docker))

if args.fhash:
    print(getFileHash(args.fhash))

if args.ghash:
    print(getGitHash(args.ghash))

if args.release:
    print(getGitRelease(args.release))

if args.gitlab:
    print(getGitlabRelease(args.gitlab))

if args.cargo:
    print(getCargoRelease(args.cargo))

if args.list:
    try:
        splitargs = args.list.split(",")
        nme = splitargs[0]
        uri = splitargs[1]
        ext = splitargs[2]
    except IndexError:
        exit("Not enough , seperated arguments passed to --list")
    print(getHTTPRelease(uri, nme, ext))

if args.ftp:
    try:
        splitargs = args.ftp.split(",")
        nme = splitargs[0]
        uri = splitargs[1]
        dir = splitargs[2]
        ext = splitargs[3]
    except IndexError:
        exit("Not enough , seperated arguments passed to --ftp")
    print(getFTPRelease(uri, dir, nme, ext))
