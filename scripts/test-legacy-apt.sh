#!/bin/sh
set -eu
# Run inside a disposable Ubuntu container with /repo mounted read-only.
mkdir /tmp/repo
cp -R /repo/pool /repo/Packages /repo/Packages.gz /repo/Release /repo/Release.gpg /tmp/repo/
apt-key add /repo/Release.key
printf 'deb file:/tmp/repo ./\n' > /tmp/retrotube.list
mkdir -p /tmp/lists/partial
apt-get --version | head -1
apt-get -o Dir::Etc::sourcelist=/tmp/retrotube.list -o Dir::Etc::sourceparts=- -o Dir::State::lists=/tmp/lists -o APT::Architecture=iphoneos-arm update
cd /tmp
apt-get -o Dir::Etc::sourcelist=/tmp/retrotube.list -o Dir::Etc::sourceparts=- -o Dir::State::lists=/tmp/lists -o APT::Architecture=iphoneos-arm download com.retrotube.app
sha256sum /tmp/*.deb
