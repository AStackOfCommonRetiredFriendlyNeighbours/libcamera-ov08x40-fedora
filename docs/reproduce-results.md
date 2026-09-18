# Reproduce the September 18 camera result

Tested on one HP Spectre x360 14 (2024), Intel Meteor Lake/IPU6, OV08X40,
Fedora 44 KDE, kernel 7.2.5-200.fc44.x86_64, libcamera
0.7.1-1.hpfix2.fc44, PipeWire 1.6.8 and Mesa 26.2.2. Other sensors and lighting
conditions are untested. This is practical indoor tuning, not a calibrated CCM.

## 1. Build and install the backport

From the repository root, in a terminal in your desktop session:

```bash
sudo dnf install rpm-build rpmdevtools dnf-plugins-core python3-pyyaml v4l-utils pipewire-plugin-libcamera libcamera libcamera-ipa
sudo dnf builddep ./libcamera.spec
RPMBUILD_ROOT="$HOME/rpmbuild-ov08x40" ./scripts/build.sh
RPMBUILD_ROOT="$HOME/rpmbuild-ov08x40" ./scripts/install.sh
```

Use a build directory containing only one RPM build; the installer rejects
multiple candidates. Review the DNF transaction. All installed libcamera
subpackages must have matching versions. Do not downgrade a newer libcamera
blindly: this patch set specifically targets 0.7.1, and newer releases may
already contain some changes. Existing users of hpfix2 can skip rebuilding.

## 2. Apply the final user profile

Close camera applications and finish any audio/video calls first. The installer
restarts WirePlumber, which briefly interrupts multimedia devices. Run as your
ordinary desktop user, without sudo:

```bash
./scripts/install-user-fix.py --dry-run
./scripts/install-user-fix.py
```

The installer copies the tracked profile into your user configuration, merges
its IPA search path into existing libcamera YAML, installs the sensor helper,
and enables its login service. It preserves unrelated YAML settings, although
YAML comments/formatting are not preserved. Every replaced file is backed up
under `${XDG_STATE_HOME:-$HOME/.local/state}/ov08x40-fix/backups/`; the printed
backup directory includes a manifest recording previously absent files too.
Reinstalling creates another backup. Repository files are copied, not linked;
rerun the installer after changing them.

The final settings are:

| Setting | Final value |
| --- | --- |
| Sensor digital gain | 1024 = 1× (previously 2560 = 2.5×) |
| Maximum analogue gain | 3× (previous running setup allowed 6×) |
| Maximum exposure | 40 ms (previously 33 ms; hardware/frame interval may limit it further) |
| AGC target | 2.1 (previously 2.3) |
| Gamma | 2.1 (previously 2.2) |
| Contrast | 1.20 (previously 1.15) |
| Colour matrix | Exact coefficients in `config/ov08x40.yaml` |

The matrix increases blue and slightly reduces green relative to the earlier
profile. The owner confirmed less yellow-green cast and improved grain in
Snapshot; the final image was darker. Lower gain does not implement denoising.
Longer exposure can cause motion blur or lower frame rates. Bright lights behind
the subject still clip; front lighting improves the result without more gain.

## 3. Verify

Reopen Snapshot (Camera), leave it running for several seconds, and inspect:

```bash
systemctl --user is-enabled ov08x40-gain.service
systemctl --user status ov08x40-gain.service --no-pager
journalctl --user -u wireplumber -b --no-pager | grep -E 'Using tuning file|IPASoft: Exposure'
```

Expect `active (exited)` for the successful oneshot service, the user profile
path ending in `libcamera/ipa/simple/ov08x40.yaml`, and `gain 1-3` once streaming.
The service journal identifies the actual sensor device. Verify its controls:

```bash
for sensor in /sys/class/video4linux/v4l-subdev*; do
    case "$(cat "$sensor/name")" in
        'ov08x40 '*) v4l2-ctl -d "/dev/${sensor##*/}" --get-ctrl=digital_gain,analogue_gain,exposure ;;
    esac
done
```

Expect `digital_gain: 1024`; analogue gain uses register units (384 = 3×).
Do not hard-code `/dev/v4l-subdev6`: numbering can change. A 90-frame 1080p
PipeWire stream completed successfully on the tested machine with this profile.
Browser/conferencing processing can still differ from Snapshot.

## Persistence and updates

The service applies digital gain at login, before WirePlumber when both are
started in the same systemd transaction. It retries sensor access for 20 seconds.
The tuning files persist in user configuration and normal RPM updates do not
overwrite them. The service is not a hotplug or resume watcher. After a driver
reload, device reset, or resume that resets gain, reapply with:

```bash
systemctl --user restart ov08x40-gain.service
```

Check gain after suspend/resume; automatic reapplication there has not been
validated. If another program changes digital gain, it also needs reapplying.
Fedora updates can replace the backport or change tuning compatibility. Verify
the package versions, tuning log and gain after such updates; do not assume
that user files alone replace the required backport. No package locks are set.

## Undo just this user profile

Close camera apps. Disable the login service and restore the driver default:

```bash
systemctl --user disable --now ov08x40-gain.service
for sensor in /sys/class/video4linux/v4l-subdev*; do
    case "$(cat "$sensor/name")" in
        'ov08x40 '*) v4l2-ctl -d "/dev/${sensor##*/}" --set-ctrl=digital_gain=2560 ;;
    esac
done
```

Use the printed backup directory's `manifest.json`: for each entry with
`existed: true`, copy its named backup to its recorded `path`; for an entry with
`existed: false`, remove the installed file at that path. Use the earliest backup
to undo the first installation, or the most recent to undo only the last update.
Inspect later edits before restoring a whole configuration file. If there was a
previous gain service you intend to retain, re-enable/restart that restored
service instead of leaving it disabled. Then run:

```bash
systemctl --user daemon-reload
systemctl --user restart wireplumber
```

For RPM rollback as well, follow [rollback.md](rollback.md).

## What the investigation established

The hpfix2 libraries and sensor tuning were still installed when the image
regressed. CPU processing did not improve the image, so that experiment was
removed; there is no CPU override in this profile. Reducing digital gain and
then applying the new colour/exposure profile improved the result according to
the owner. The investigation did not establish which update caused the problem.
No personal camera images are included in this repository.

## Repository checks

```bash
python3 tests/test_user_profile.py
systemd-analyze --user verify systemd/ov08x40-gain.service
```

The installer checks use temporary directories and mock service calls; they do
not change your camera configuration. They cover dry-run behavior, config merging,
backups, repeated installation, executable permissions and symlink protection.
