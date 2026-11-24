RetroTube Cydia repository

The flat APT endpoint is https://rtn68tg94j-del.github.io/RetroTube-Repo/ .
The source entry is `deb https://rtn68tg94j-del.github.io/RetroTube-Repo/ ./`.

Packages target iphoneos-arm (ARMv7) and iOS 9.0 or later, including iOS 9.3.5.
RetroTube 0.1.1 is included. Its existing package identifier enables Cydia upgrades.

Repository signatures use RSA-3072 and SHA-256 with OpenPGP v4 signatures.
The public signing key is Release.asc. Its fingerprint is
`79F6 0B95 C379 9F2E 8369 5EE6 8FCB 1EDF 6099 E2C4`.
The key expires on 2028-11-23 and must be renewed before that date.

Download and inspect Release.asc on a trusted computer, then transfer it through an existing secure channel without opening it in Safari or iFile preview.
Before adding the source, import Release.asc into the device's APT trusted keyring.
Download it over verified HTTPS, inspect the fingerprint using `gpg --with-fingerprint Release.asc`,
compare it against the fingerprint above, then run `apt-key add Release.asc` as root.
Cydia's add-source dialog alone does not establish trust in a custom signing key.

Packages.gz uses ordinary gzip. Packages includes MD5, SHA-1 and SHA-256 hashes.
Release signs the indexes and their sizes. Release.gpg supports older APT clients.
InRelease supports clients with inline signature support.
No trusted=yes, unauthenticated installation or TLS verification overrides are used.

GitHub Pages must be enabled under Settings → Pages with GitHub Actions as the source.
The public workflow verifies all signatures and hashes before deploying only APT files.
HTTPS certificate trust on an actual iOS 9.3.5 device still requires device testing.
No device TLS verification setting should be disabled.

Automatic updates originate in the private RetroTube repository after a successful build.
Configure two Actions secrets there. APT_REPO_TOKEN must be a fine-grained GitHub token
limited to this public repository with Contents read/write. APT_SIGNING_KEY contains the
armored private signing key matching Release.asc. Keep both values out of this repository.
The source workflow downloads only the verified DEB artifact. It rejects overwriting an
existing filename with different bytes. Bump the application version for each release.
The public repository does not require secrets.

Locally, run `python3 scripts/build.py` with the signing key available in GNUPGHOME,
copy the generated index and signature files from _site into the repository root,
then run `python3 scripts/verify.py`.

Validation on 2026-11-24 passed with APT 0.8.16 (Ubuntu 12.04) using
Release.gpg, and APT 1.0.1 (Ubuntu 14.04) using InRelease.
Both clients authenticated the metadata and retrieved version 0.1.1 for iphoneos-arm.
These container checks cover repository formats and signatures. They do not emulate
Cydia's exact patched APT build or the iOS certificate trust store.

The former Release.key URL is retired because its extension was served as
application/vnd.apple.keynote. Release.asc must be served as application/pgp-keys.
Deployment verifies the actual HTTP Content-Type and the unchanged key bytes.
The new extension does not change the signing key or its fingerprint.
