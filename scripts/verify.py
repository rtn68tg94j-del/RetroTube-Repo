"""Validate published indexes, signed Release and every referenced package."""
import argparse
import gzip
import hashlib
from pathlib import Path
import subprocess
import tempfile
from signing_policy import verify_public_key

parser = argparse.ArgumentParser()
parser.add_argument("root", nargs="?", type=Path, default=Path(__file__).resolve().parent.parent)
root = parser.parse_args().root.resolve()
key = verify_public_key(root)
with tempfile.TemporaryDirectory() as temporary:
    home = Path(temporary)
    home.chmod(0o700)
    subprocess.run(["gpg", "--homedir", str(home), "--batch", "--import", str(root / "Release.asc")], check=True)
    fingerprint = subprocess.check_output(
        ["gpg", "--homedir", str(home), "--with-colons", "--list-keys"], text=True
    )
    assert key in fingerprint
    for args in [[str(root / "Release.gpg"), str(root / "Release")], [str(root / "InRelease")]]:
        status = subprocess.check_output(
            ["gpg", "--homedir", str(home), "--batch", "--status-fd", "1", "--verify", *args],
            text=True,
        )
        assert f"[GNUPG:] VALIDSIG {key} " in status
        valid = [line.split() for line in status.splitlines() if line.startswith("[GNUPG:] VALIDSIG ")]
        assert len(valid) == 1 and valid[0][9] == "8", "Release signature must use SHA-256"
        assert "[GNUPG:] GOODSIG " in status
        assert "[GNUPG:] EXPKEYSIG " not in status
    clear = subprocess.check_output(["gpg", "--homedir", str(home), "--batch", "--decrypt", str(root / "InRelease")])
    assert clear == (root / "Release").read_bytes()

release = (root / "Release").read_text()
sha256 = release.split("SHA256:\n", 1)[1].strip().splitlines()
assert len(sha256) == 2
for line in sha256:
    digest, size, filename = line.split()
    assert filename in ("Packages", "Packages.gz")
    data = (root / filename).read_bytes()
    assert len(data) == int(size) and hashlib.sha256(data).hexdigest() == digest
assert gzip.decompress((root / "Packages.gz").read_bytes()) == (root / "Packages").read_bytes()
referenced = set()
for stanza in (root / "Packages").read_text().strip().split("\n\n"):
    fields = dict(line.split(": ", 1) for line in stanza.splitlines() if not line.startswith(" "))
    assert fields["Package"] == "com.retrotube.app"
    assert fields["Architecture"] == "iphoneos-arm"
    filename = Path(fields["Filename"])
    assert filename.parts[0] == "pool" and len(filename.parts) == 2 and filename.suffix == ".deb"
    referenced.add(filename.name)
    data = (root / filename).read_bytes()
    assert int(fields["Size"]) == len(data)
    for key, algorithm in [("MD5sum", "md5"), ("SHA1", "sha1"), ("SHA256", "sha256")]:
        assert fields[key] == hashlib.new(algorithm, data).hexdigest()
assert referenced == {p.name for p in (root / "pool").glob("*.deb")}
print("Release signatures, index hashes and all DEB checksums verified.")
