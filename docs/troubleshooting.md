# Troubleshooting

## The build script reports missing commands

Install Fedora's standard RPM tools, then install build dependencies:

```bash
sudo dnf install rpm-build rpmdevtools dnf-plugins-core
sudo dnf builddep ./libcamera.spec
```

The build script does not install dependencies because that would modify the
system and require root privileges.

## Source download fails

`scripts/build.sh` uses `spectool -g` on the spec's normal Source URL. Check
network access and confirm the URL expanded by:

```bash
spectool -S ./libcamera.spec
```

You may also place the exact `libcamera-v0.7.1.tar.bz2` source in
`$RPMBUILD_ROOT/SOURCES`; the repository deliberately does not bundle it.

## A patch no longer applies

This set targets Fedora's libcamera 0.7.1 source. In particular, patch 0003 is
adapted to that version's older AGC implementation. Do not blindly refresh it
against a newer Fedora build: first check whether some or all changes have been
merged upstream, then document any new backport.

To isolate preparation failures:

```bash
topdir=${RPMBUILD_ROOT:-$HOME/rpmbuild}
mkdir -p "$topdir/TMP"
rpmbuild --define "_topdir $topdir" --define "_tmppath $topdir/TMP" \
  -bp ./libcamera.spec
```

Reject and backup files (`*.rej`, `*.orig`) are ignored by Git, but should be
examined rather than committed.

## The camera still uses uncalibrated tuning

Confirm that the matching `libcamera-ipa` custom RPM is installed and contains
the tuning file:

```bash
rpm -q libcamera libcamera-ipa libcamera-v4l2
rpm -ql libcamera-ipa | grep '/ov08x40.yaml$'
journalctl --user -b | grep -Ei 'libcamera|ov08x40|ipa|camera'
```

Restart all camera clients or log out and in. Expected paths can vary by build,
but the log should mention an OV08X40 tuning file rather than
`uncalibrated.yaml`.

## DNF reports package conflicts

Do not force individual RPMs. libcamera subpackages require the exact main
package version/release. Rebuild a consistent set, close applications using the
libraries, and use `scripts/install.sh` to choose matching installed
subpackages. Carefully review the DNF preview.

## Image quality differs

The CCM and exposure choices were tested under warm indoor lighting on one
machine and are not calibrated for every module. Compare a direct libcamera
client with browser/conferencing output: those applications may add processing,
scaling, or compression. Remaining static-properties or kernel warnings do not
necessarily mean the tuning file was skipped.

## Final profile does not load or digital gain resets

Use [the reproduction guide](reproduce-results.md#3-verify) to check the selected
user tuning path and actual digital gain. The final profile requires the backport;
copying YAML onto an unpatched libcamera may not implement its AGC/Adjust controls.
`LIBCAMERA_IPA_CONFIG_PATH` or `LIBCAMERA_SIMPLE_TUNING_FILE` environment overrides
can take precedence over the configured search path. Existing CPU overrides are
preserved by the installer but were not needed for the tested result.

The oneshot service may fail if the sensor is missing, permissions are unavailable,
or v4l-utils is absent. Inspect `journalctl --user -u ov08x40-gain.service -b`.
Run the installer inside the desktop session, not via sudo or an unrelated SSH
session. Reapply the service after any device reset that restores digital gain.
