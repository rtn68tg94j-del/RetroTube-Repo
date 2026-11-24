# RetroTube Test signing key

Public fingerprint: `06C735FB8C1F3BAE431234116EB7D1B4C0AA7115`.
RSA-3072 signing/certification key; SHA-256; expires 2029-11-23.
The private key has no passphrase for noninteractive Actions signing. It is not in Git, CI logs or artifacts.

Create the repository Actions secret `APT_SIGNING_KEY_TEST` in **rtn68tg94j-del/RetroTube**, Settings → Secrets and variables → Actions → New repository secret. Paste the complete private ASCII armor supplied separately, including BEGIN/END lines. `APT_REPO_TOKEN` remains necessary for automated pushes. The stable source's `APT_SIGNING_KEY` is separate and unchanged.

The app publication workflow checks the private fingerprint after import, and `scripts/build.py` checks both the public and private fingerprints before writing output. `scripts/verify.py` requires the correct source-specific fingerprint and SHA-256 Release signatures. Stable uses `79F60B95C3799F2E83695EE68FCB1EDF6099E2C4`; `/test/` uses the new key. Swapping them fails validation.

On a trusted computer, obtain `/test/Release.asc` over HTTPS and inspect:

```
gpg --show-keys --with-fingerprint RetroTube-Test-Release.asc
```

Compare the full fingerprint above, transfer that **public** file to iPad using your existing secure channel, then in an existing trusted root terminal run:

```
apt-key add /path/to/RetroTube-Test-Release.asc
```

Keep the stable key installed. Refresh Cydia sources and use `https://rtn68tg94j-del.github.io/RetroTube-Repo/test/`. Do not disable signature checking. The legacy APT trust store is global; source separation is also enforced by the repository signing and verification configuration. The private key is never needed on iPad.
