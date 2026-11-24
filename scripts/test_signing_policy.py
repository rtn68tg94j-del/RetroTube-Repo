"""Check the two pinned trust roots, including rejection of swapped public keys."""
from pathlib import Path
import tempfile
from unittest.mock import patch
import shutil
import signing_policy as policy

repository = policy.REPOSITORY
with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp)
    (root / "test").mkdir()
    for source in ("Release.asc", "test/Release.asc"):
        shutil.copyfile(repository / source, root / source)
    with patch.object(policy, "REPOSITORY", root):
        assert policy.verify_public_key(root) == policy.STABLE_KEY
        assert policy.verify_public_key(root / "test") == policy.TEST_KEY
        shutil.copyfile(root / "Release.asc", root / "test/Release.asc")
        try:
            policy.verify_public_key(root / "test")
        except ValueError:
            pass
        else:
            raise AssertionError("Test source accepted the stable public key")
        shutil.copyfile(repository / "test/Release.asc", root / "Release.asc")
        try:
            policy.verify_public_key(root)
        except ValueError:
            pass
        else:
            raise AssertionError("Stable source accepted the test public key")
print("PASS separate stable/test fingerprints and rejection of swapped keys")
