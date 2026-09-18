# Patch provenance

The table describes the exact files used by the working RPM build. SHA-256
digests are included so later edits are visible. “Upstream” below means supplied
as a libcamera mailing-list/Patchwork message, not necessarily merged.

| Order | Repository file | Author / original subject | Recorded source | Fedora? | Local adaptation? | Purpose and metadata status |
|---:|---|---|---|---|---|---|
| 1 | `0001-disable-rpi-pisp.patch` | No author or subject in the file | Present in Fedora `libcamera-0.7.1-1.fc44` source RPM | Yes | No local change detected | Comments out the `rpi/pisp` pipeline to keep the Fedora build working. Headerless diff; no authorship or sign-off metadata exists in the local file. |
| 2 | `0002-simple-adjust-tuning.patch` | James Alexander; “ipa: simple: adjust: Read defaults from tuning” | [libcamera Patchwork ID 27775](https://patchwork.libcamera.org/patch/27775/); message ID `<20260816204259.2845517-2-opensource@inspiredexperts.com>` | No evidence it came from Fedora | No local modification detected | Reads gamma, contrast, and saturation defaults from Simple IPA tuning. Full mail header, `Signed-off-by`, and `Acked-by` retained. |
| 3 | `0003-simple-agc-tuning-f44-backport.patch` | Upstream concept and original patch: James Alexander, “ipa: simple: agc: Read limits from tuning”; author of the local adaptation is **not identified** | [libcamera Patchwork ID 27776](https://patchwork.libcamera.org/patch/27776/); message ID `<20260816204259.2845517-3-opensource@inspiredexperts.com>` | No evidence it came from Fedora | **Yes. Fedora/libcamera 0.7.1-specific backport, not the original upstream patch** | Fedora 0.7.1 used an older approximately 10-percent step exposure/gain controller, so the upstream patch did not apply cleanly. The local patch retains that controller and backports the tuning interface for `target`, `maxAnalogueGain`, and `maxExposureTimeMs`. It has no mail header or `Signed-off-by`; no authorship is inferred for the adaptation. |
| 4 | `0004-ov08x40-spectre-tuning.patch` | James Alexander; “ipa: simple: Add OV08X40 tuning” | [libcamera Patchwork ID 27777](https://patchwork.libcamera.org/patch/27777/); message ID `<20260816204259.2845517-4-opensource@inspiredexperts.com>` | No evidence it came from Fedora | No local modification detected | Installs `ov08x40.yaml` with CCM, Adjust, and AGC values used on the tested Spectre. Full mail header and `Signed-off-by` retained; YAML is marked `CC0-1.0`. |
| 5 | `0005-ov08x40-sensor-helper.patch` | Upstream author/concept source: Bogdan Radulescu, “ipa: libipa: camera_sensor_helper: add ov08x40”; author of the local adaptation is **not identified** | [libcamera Patchwork ID 26747](https://patchwork.libcamera.org/patch/26747/) and its upstream review/follow-up discussion | No evidence it came from Fedora | **Yes. Fedora 0.7.1 backport; not the original upstream patch artifact** | Adds the helper required for Simple IPA AGC, with black level 4096 and gain mapping `AnalogueGainLinear{ 1, 0, 0, 128 }` (`register_value / 128`). It follows the reviewed v2 source change, including alphabetical placement after `imx708` and before `ov2685`, but uses Fedora 0.7.1-compatible diff context. The local file has no mail header, `Signed-off-by`, or `Reviewed-by`, so none was added. |

## Exact input digests

```text
ddd2f9fd1a1a41ccc1065368e6f91c8edce3d836fcce9805d86a7f9f387ebffb  0001-disable-rpi-pisp.patch
4dc5be55e031a5fc92e099b67db2feb252cb3b073132a3dc394db0b95964aa2f  0002-simple-adjust-tuning.patch
cd913a97e67b5a03577a9dc7f66e95fa236e9bcea4f12f1f3728a8ab4a4d6109  0003-simple-agc-tuning-f44-backport.patch
608e7982ddaf6727a69357a6adcbc51a1674fa1901e0916482e668540bc2852f  0004-ov08x40-spectre-tuning.patch
e62613ab544d3e053263b0f6cb4ab18e988cef5fbe0a56324b403e9c826f131c  0005-ov08x40-sensor-helper.patch
```

## Fedora packaging baseline

The local source RPM is `libcamera-0.7.1-1.fc44.src.rpm`, reported as packaged
by Fedora Project and signed with key ID `dbfcf71c6d9f90a6`. Its payload contains
the upstream tarball, the spec, patch 0001, and the three files reproduced under
`packaging/`. The custom spec changes the release to `1.hpfix2%{?dist}` and adds
patches 0002–0005. `%autosetup -p1` applies `Patch01` through `Patch05` in numeric
declaration order during `%prep`.

The spec builds the main `libcamera` package plus `devel`, `ipa`, `tools`,
`qcam`, `gstreamer`, `v4l2`, and `python3-libcamera` subpackages.

## Upstream comparison details

### Patch 0003

Patchwork 27776 is the conceptual source and is authored by James Alexander.
The upstream patch targets a newer proportional AGC implementation: it replaces
an error calculation based on `kExposureOptimal`. Fedora/libcamera 0.7.1 instead
has separate approximately 10-percent step-up and step-down branches. The local
patch therefore changes those branch thresholds to use a configurable target
while leaving their step logic intact, and adapts the upstream `init()` and
`configure()` tuning interface to the older source. It is not the original
Patchwork patch, and its headerless form provides no evidence identifying the
person who performed the adaptation.

### Patch 0005

Patchwork 26747 is authored by Bogdan Radulescu. It explains that Simple IPA
cannot run AGC for OV08X40 without a sensor helper and derives the analogue-gain
mapping from the kernel driver's register range and unity value: the multiplier
is `register_value / 128`, represented by
`AnalogueGainLinear{ 1, 0, 0, 128 }`. Review requested removal of the explanatory
code comment, addition of a black level, and alphabetical placement. The author
reported that v2 adds `blackLevel_ = 4096` (a 10-bit `0x40` pedestal scaled to
the helper's 16-bit representation) and moves the entry before `ov2685`.

The regenerated local 0005 contains the same 11 added source lines as the
substantive v2 helper, including its tab indentation, black level, gain mapping,
and alphabetical placement after `imx708` and before `ov2685`. It is still not
the original upstream patch artifact: its hunk is generated against Fedora
0.7.1, and it omits v2's commit message, change log, `Signed-off-by`, and review
metadata. Those omissions are preserved rather than retroactively adding
attribution trailers to a headerless local adaptation.

## Remaining provenance notes

- The exact person who performed the local Fedora 0.7.1 adaptation in patch
  0003 is not recorded.
- The exact person who regenerated or adapted patch 0005 for Fedora 0.7.1 is
  not recorded.
- No additional `Signed-off-by` should be added retroactively without
  identifying and obtaining approval from the actual adapter.
- The upstream merge status of Patchwork IDs 27775, 27776, 27777, and 26747
  should be monitored over time because this repository may become unnecessary
  as the fixes land upstream.

Fedora packaging licensing and provenance are documented in
`LICENSES/README.md`.

## September 18 local runtime profile

`config/ov08x40.yaml` derives from the CC0 tuning in patch 0004. It records a
subsequent local, photograph-guided adjustment: CCM rows scaled by 1.04, 0.94,
and 1.35 respectively, contrast 1.20, gamma 2.1, AGC target 2.1, maximum analogue
gain 3.0 and maximum exposure 40 ms. The earlier live installation had raised
maximum analogue gain to 6.0. These changes are local tuning, not an upstream
submission or laboratory calibration; patch 0004 and its attribution are intact.

The new helper/service set the OV08X40 digital gain control to 1024 (unity).
The user confirmed improved results, but update causality was not established.
See [the reproduction guide](reproduce-results.md) for exact scope and limitations.
