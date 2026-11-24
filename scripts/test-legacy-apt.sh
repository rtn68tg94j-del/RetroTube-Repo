#!/bin/sh
set -eu
# Run inside a disposable Ubuntu container with /repo mounted read-only.
repo_root=${1:-/repo}
expected_version=${2:-0.1.1}
mkdir /tmp/repo
cp -R "$repo_root/pool" "$repo_root/Packages" "$repo_root/Packages.gz" "$repo_root/Release" "$repo_root/Release.gpg" /tmp/repo/
apt-key add "$repo_root/Release.asc"
printf 'deb file:/tmp/repo ./\n' > /tmp/retrotube.list
mkdir -p /tmp/lists/partial
apt-get --version | head -1
apt-get -o Dir::Etc::sourcelist=/tmp/retrotube.list -o Dir::Etc::sourceparts=- -o Dir::State::lists=/tmp/lists -o APT::Architecture=iphoneos-arm update
apt-cache -o Dir::Etc::sourcelist=/tmp/retrotube.list -o Dir::Etc::sourceparts=- -o Dir::State::lists=/tmp/lists -o APT::Architecture=iphoneos-arm policy com.retrotube.app > /tmp/retrotube-policy
cat /tmp/retrotube-policy
grep -Fx "  Candidate: $expected_version" /tmp/retrotube-policy
cd /tmp
apt-get -o Dir::Etc::sourcelist=/tmp/retrotube.list -o Dir::Etc::sourceparts=- -o Dir::State::lists=/tmp/lists -o APT::Architecture=iphoneos-arm download "com.retrotube.app=$expected_version"
sha256sum /tmp/*.deb
cmp "$repo_root/pool/com.retrotube.app_${expected_version}_iphoneos-arm.deb" "/tmp/com.retrotube.app_${expected_version}_iphoneos-arm.deb"
