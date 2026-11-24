"""Generate and verify a flat, signed APT repository for legacy Cydia."""
import gzip
import hashlib
import os
from pathlib import Path
import shutil
import struct
import subprocess
import tempfile
from email.utils import formatdate

root = Path(__file__).resolve().parent.parent
os.chdir(root)
site = root / "_site"
if site.exists():
    shutil.rmtree(site)
(site / "pool").mkdir(parents=True)
packages = sorted((root / "pool").glob("*.deb"))
assert packages, "No DEB packages"
for package in packages:
    fields = subprocess.check_output(
        ["dpkg-deb", "-f", str(package), "Package", "Architecture", "Version"], text=True
    )
    assert "Package: com.retrotube.app" in fields
    assert "Architecture: iphoneos-arm" in fields
    with tempfile.TemporaryDirectory() as directory:
        subprocess.run(["dpkg-deb", "-x", str(package), directory], check=True)
        app = Path(directory) / "Applications/RetroTube.app"
        binary = (app / "RetroTube").read_bytes()
        magic, cpu, subtype = struct.unpack_from("<III", binary)
        assert (magic, cpu, subtype & 0xFFFFFF) == (0xFEEDFACE, 12, 9), "Expected thin ARMv7"
        minimum = None
        offset = 28
        for _ in range(struct.unpack_from("<I", binary, 16)[0]):
            command, size = struct.unpack_from("<II", binary, offset)
            assert size >= 8
            if command == 0x25:  # LC_VERSION_MIN_IPHONEOS
                minimum = struct.unpack_from("<I", binary, offset + 8)[0]
            offset += size
        assert minimum is not None and minimum <= 0x090305
    shutil.copyfile(package, site / "pool" / package.name)

index = subprocess.check_output(["dpkg-scanpackages", "--multiversion", "pool", "/dev/null"])
(site / "Packages").write_bytes(index)
(site / "Packages.gz").write_bytes(gzip.compress(index, mtime=0))
for stanza in index.decode().strip().split("\n\n"):
    fields = dict(line.split(": ", 1) for line in stanza.splitlines() if not line.startswith(" "))
    data = (site / fields["Filename"]).read_bytes()
    assert len(data) == int(fields["Size"])
    for field, algorithm in [("MD5sum", "md5"), ("SHA1", "sha1"), ("SHA256", "sha256")]:
        assert hashlib.new(algorithm, data).hexdigest() == fields[field]
assert gzip.decompress((site / "Packages.gz").read_bytes()) == index

release = [
    "Origin: RetroTube",
    "Label: RetroTube",
    "Suite: stable",
    "Version: 1.0",
    "Codename: retrotube",
    "Architectures: iphoneos-arm",
    "Description: RetroTube native video player for legacy iOS",
    "Date: " + formatdate(usegmt=True),
]
for field, algorithm in [("MD5Sum", "md5"), ("SHA1", "sha1"), ("SHA256", "sha256")]:
    release.append(field + ":")
    for filename in ["Packages", "Packages.gz"]:
        data = (site / filename).read_bytes()
        release.append(f" {hashlib.new(algorithm, data).hexdigest()} {len(data)} {filename}")
(site / "Release").write_text("\n".join(release) + "\n")
shutil.copyfile(root / "Release.asc", site / "Release.asc")
(site / ".nojekyll").touch()
key = "79F60B95C3799F2E83695EE68FCB1EDF6099E2C4"
common = ["gpg", "--batch", "--yes", "--local-user", key, "--digest-algo", "SHA256"]
subprocess.run(common + ["--armor", "--detach-sign", "--output", str(site / "Release.gpg"), str(site / "Release")], check=True)
subprocess.run(common + ["--clearsign", "--output", str(site / "InRelease"), str(site / "Release")], check=True)
with tempfile.TemporaryDirectory() as directory:
    keyring = Path(directory) / "trusted.gpg"
    subprocess.run(["gpg", "--batch", "--yes", "--dearmor", "--output", str(keyring), str(site / "Release.asc")], check=True)
    for args in [
        [str(site / "Release.gpg"), str(site / "Release")],
        [str(site / "InRelease")],
    ]:
        subprocess.run(["gpg", "--batch", "--no-default-keyring", "--keyring", str(keyring), "--verify", *args], check=True)
print("Verified ARMv7, iOS minimum, DEB hashes, gzip index and both Release signatures.")
