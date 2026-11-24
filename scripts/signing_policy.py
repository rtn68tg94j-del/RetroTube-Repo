"""Pinned, separate trust roots for stable and test; no private material."""
from pathlib import Path
import subprocess

STABLE_KEY = "79F60B95C3799F2E83695EE68FCB1EDF6099E2C4"
TEST_KEY = "7AF9259478D132C9B9D3C49B0CED4FE24D33F058"
REPOSITORY = Path(__file__).resolve().parent.parent

def expected_key(root):
    root = Path(root).resolve()
    if root == REPOSITORY:
        return STABLE_KEY
    if root == REPOSITORY / "test":
        return TEST_KEY
    raise ValueError("Only the stable root and its test/ source are supported")

def fingerprints(colons):
    return [line.split(":")[9] for line in colons.splitlines() if line.startswith("fpr:")]

def verify_public_key(root):
    key = expected_key(root)
    data = subprocess.check_output(["gpg", "--batch", "--with-colons", "--show-keys", str(Path(root) / "Release.asc")], text=True)
    if fingerprints(data) != [key]:
        raise ValueError("Unexpected public key fingerprint for this source")
    return key

def verify_signing_key(root):
    key = verify_public_key(root)
    data = subprocess.check_output(["gpg", "--batch", "--with-colons", "--list-secret-keys", key + "!"], text=True)
    if fingerprints(data) != [key] or not any(line.startswith("sec:") for line in data.splitlines()):
        raise ValueError("Required source-specific private signing key is unavailable")
    return key
