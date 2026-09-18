# libcamera OV08X40 tuning for Fedora

An experimental Fedora 44 RPM patch set for the OV08X40 camera on one HP
Spectre x360 14 (2024, Intel Meteor Lake/IPU6). It improves the libcamera
Simple IPA path on that machine. It is not a universal HP webcam fix.

## Why it exists

The camera was detected through libcamera, PipeWire and WirePlumber, but the
image had a strong green/yellow cast and poor exposure/gain behaviour. Logs
showed that libcamera could not find `ov08x40.yaml`, had no static properties
for the sensor, and could not create an OV08X40 sensor helper.

## Tested hardware

- HP Spectre x360 14, 2024 generation
- Intel Meteor Lake / Intel IPU6 camera stack
- OV08X40 image sensor
- Fedora 44
- Fedora libcamera base `0.7.1-1.fc44`

Other OV08X40/IPU6 systems are untested. See [docs/hardware.md](docs/hardware.md).

## What changes

The RPM keeps Fedora's 0.7.1 packaging and applies five patches in order:

1. Fedora's existing temporary Raspberry Pi PiSP build-disable patch.
2. Simple IPA `Adjust` defaults read from tuning.
3. A **local Fedora-0.7.1 backport/adaptation** of AGC tuning controls while
   retaining the older approximately 10-percent step controller.
4. An OV08X40 tuning file for the tested Spectre.
5. A Fedora-0.7.1 backport of Bogdan Radulescu's upstream OV08X40
   `CameraSensorHelper` concept, with the reviewed linear analogue-gain mapping
   (`AnalogueGainLinear{ 1, 0, 0, 128 }`), black level (`4096`), and alphabetical
   placement.

Full attribution and uncertainty are in
[docs/patch-provenance.md](docs/patch-provenance.md).

## Reproduce the latest tested result

The RPM backport alone is not the final camera setup. Follow
[the complete reproduction guide](docs/reproduce-results.md) to build/install
hpfix2, apply the September 18 user profile, enable 1× digital gain at login,
and verify or undo the result. Existing hpfix2 users can skip rebuilding and run:

```bash
sudo dnf install python3-pyyaml v4l-utils
./scripts/install-user-fix.py --dry-run
./scripts/install-user-fix.py
```

Close camera apps/calls first: installation restarts WirePlumber. The installer
backs up affected files and preserves unrelated libcamera configuration keys.
The final profile reduced the yellow-green cast and grain on the tested machine,
with a darker image from lower gain. Its colour matrix is specific to the tested
indoor scene; identical results on other hardware or lighting are not promised.
The login service is not a resume/hotplug watcher; see the guide for reapplying it.

## Build

Install RPM build tooling and the spec's build dependencies. On Fedora, the
usual starting point is:

```bash
sudo dnf install rpm-build rpmdevtools dnf-plugins-core
sudo dnf builddep ./libcamera.spec
```

Then build as an ordinary user:

```bash
./scripts/build.sh
```

The script uses `~/rpmbuild` by default. Set `RPMBUILD_ROOT` to choose another
RPM build tree. It copies the tracked inputs there, obtains `Source0` with
`spectool`, and runs `rpmbuild -ba`; it never installs packages.

## Install

Review the generated RPMs, then run:

```bash
./scripts/install.sh
```

The script selects only custom RPMs corresponding to installed libcamera
subpackages, excludes debug packages, prints DNF's transaction preview, and
requires explicit confirmation before invoking `sudo dnf install`. Matching
subpackages must be upgraded together because they depend on the exact same
libcamera version and release.

## Verify

After restarting applications that use the camera (or logging out and in), run:

```bash
wpctl status
journalctl --user -b | grep -Ei 'libcamera|ov08x40|ipa|camera'
rpm -qa 'libcamera*' 'python3-libcamera' | sort
```

Positive indicators include a node such as `ov08x40 [libcamera]` and a message
like `Using tuning file .../ov08x40.yaml`; with the final user profile, this
should be the user configuration path, not the RPM’s `/usr/share` path. Some kernel or
static sensor-property warnings remained during testing.

Image quality from libcamera improved substantially on the tested machine.
Teams and browsers can still add their own scaling, processing, and compression;
this project does not claim to fix their output quality.

## Rollback

See [docs/rollback.md](docs/rollback.md) for repository-based DNF rollback.
Future Fedora updates may supersede this patch set.

## Known limitations and upstream status

- Only one machine and lighting environment have been tested.
- The colour matrix is practical tuning, not laboratory calibration.
- Patchwork messages for patches 0002 and 0004 are preserved, but the upstream
  acceptance/merge status of the patch set has not been verified.
- The upstream concept authors are documented for the headerless AGC and sensor
  helper backports, but the people who performed those local adaptations remain
  unidentified; no authorship or sign-off is inferred for them.

## Contributing

Please include Fedora/libcamera versions, sensor and platform details, relevant
logs, and whether every patch applies. Do not include hostnames, usernames, or
other private machine data. The issue and pull-request templates provide a
checklist.

## Licensing and disclaimer

Original repository documentation, scripts, GitHub templates, `.gitignore`, and
licensing notes are MIT licensed. This does not apply MIT to the repository as a
whole. Fedora-derived, libcamera-derived, CC0, LGPL, and unresolved material
retain the licensing and provenance documented in
[LICENSES/README.md](LICENSES/README.md).

This is experimental software. Review the patches and DNF transaction before
use, keep a rollback path, and use it at your own risk.
