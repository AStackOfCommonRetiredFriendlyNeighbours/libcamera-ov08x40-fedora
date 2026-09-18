# Licensing and provenance

This repository is a collection of material from multiple origins and under
multiple licenses. No single license applies to the repository as a whole.
In particular, the RPM `License:` fields in `libcamera.spec` describe the
software being packaged; they are not a file-level license declaration for the
spec file.

The license texts supplied in this directory are:

- `MIT.txt` — MIT License
- `LGPL-2.1-or-later.txt` — GNU Lesser General Public License version 2.1 or,
  at the recipient's option, any later version
- `CC0-1.0.txt` — Creative Commons CC0 1.0 Universal

## File-to-license mapping

Paths and globs below are relative to the repository root.

| Paths | License | Origin and provenance |
| --- | --- | --- |
| `README.md` | MIT | Original repository material. |
| `docs/*.md` | MIT | Original repository documentation. Upstream facts and attribution recorded in these files do not transfer ownership of upstream work. |
| `scripts/*.py`, `scripts/ov08x40-gain`, `systemd/*.service`, `tests/*.py` | MIT | Local user-profile installer and digital-gain service/helper. |
| `config/ov08x40.yaml` | CC0-1.0 | Local adaptation of patch 0004; see `docs/patch-provenance.md`. |
| `scripts/*.sh` | MIT | Original repository build and installation tooling. |
| `.github/**/*.md` | MIT | Original repository issue and pull-request templates. |
| `.gitignore` | MIT | Original repository material. |
| `LICENSES/README.md` | MIT | Original repository licensing documentation. |
| `packaging/70-libcamera.rules` | MIT | Copied unchanged from Fedora's libcamera packaging. Peter Robinson added the file in Fedora commit `e93461079efe8744331c57dfbcca59db257fdc29` ("Add udev rules file, minor package cleanups"). It is treated as an unlicensed Fedora Code contribution under the Fedora Project Contributor Agreement (FPCA) default MIT licensing framework. |
| `patches/0002-simple-adjust-tuning.patch` | LGPL-2.1-or-later | Derived from upstream libcamera work. Preserve the authorship, trailers, and provenance in the patch and `docs/patch-provenance.md`. |
| `patches/0003-simple-agc-tuning-f44-backport.patch` | LGPL-2.1-or-later | Local Fedora/libcamera 0.7.1-compatible adaptation of upstream libcamera work. The upstream conceptual source is James Alexander's Patchwork ID 27776; this is not the original upstream patch. No authorship is asserted here for the local adaptation. |
| `patches/0005-ov08x40-sensor-helper.patch` | LGPL-2.1-or-later | Local Fedora/libcamera 0.7.1-compatible adaptation of upstream libcamera work by Bogdan Radulescu, discussed as Patchwork ID 26747. It is not represented as a byte-for-byte upstream patch. |
| `patches/0004-ov08x40-spectre-tuning.patch` | CC0-1.0 | Tuning-data patch derived from upstream libcamera CC0-1.0 material. Preserve the patch's upstream authorship and provenance. |
| `packaging/qcam.metainfo.xml` | CC0-1.0 | Copied unchanged from Fedora's libcamera packaging. The file identifies Javier Martinez Canillas as its 2021 copyright holder and explicitly releases the metainfo XML under `metadata_license=CC0-1.0`. The `project_license` element describes qcam, not this metadata file. |

The LGPL classification above applies to the libcamera-derived material in the
listed patches. It does not make the repository maintainer the author or
copyright holder of the original upstream changes. Existing upstream authorship,
provenance, and Signed-off-by trailers remain authoritative and must not be
rewritten merely to match this repository's licensing layout.

## Unresolved or mixed provenance

The following files intentionally have no license assigned by this repository:

### `libcamera.spec`

The base file comes from Fedora's libcamera packaging. Fedora-authored,
unlicensed portions may fall under the FPCA's MIT default because the FPCA
expressly treats RPM spec files as Code. The initial Fedora import was made by
Javier Martinez Canillas in commit
`dd68389e5d3cd0163ee66733287cc7b10553112d` and was described as based on Peter
Robinson's work. This repository also contains small local modifications,
including its release suffix and patch declarations. Until the provenance and
licensing of every portion are sufficiently established, the complete spec file
is not labeled uniformly.

### `packaging/qcam.desktop`

This file was copied unchanged from Fedora's libcamera packaging. It entered
Fedora dist-git in the initial-import commit
`dd68389e5d3cd0163ee66733287cc7b10553112d`, authored by Javier Martinez
Canillas and described as based on Peter Robinson's work. The available history
does not establish whether the desktop file originated with Javier Martinez
Canillas, Peter Robinson, or another source. No license is assigned pending
manual verification.

### `patches/0001-disable-rpi-pisp.patch`

This standalone patch came from the Fedora source package and modifies upstream
libcamera build-system material carrying an explicit CC0-1.0 license. The
Fedora patch itself has incomplete authorship and licensing metadata. The
license of the modified upstream file is recorded here, but no separate license
is asserted for the standalone patch until its authorship and provenance are
verified.

## Fedora licensing framework

The FPCA default applies only to an unlicensed contribution actually created by
the submitting Fedora contributor. It does not relicense material copied from
upstream or another author, and an explicit license takes precedence. Fedora's
public dist-git history should be retained as part of the attribution record for
Fedora-derived files.

Relevant sources:

- Fedora Project Contributor Agreement:
  <https://docs.fedoraproject.org/en-US/legal/fpca/>
- Fedora libcamera package sources:
  <https://src.fedoraproject.org/rpms/libcamera>
- Detailed patch origins and upstream review links:
  `docs/patch-provenance.md`
