#!/usr/bin/env bash
set -euo pipefail

for command in rpmbuild spectool install find; do
	if ! command -v "$command" >/dev/null 2>&1; then
		printf 'error: required command not found: %s\n' "$command" >&2
		exit 1
	fi
done

script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
repo_dir=$(cd -- "$script_dir/.." && pwd)
topdir=${RPMBUILD_ROOT:-"${HOME:?HOME is not set}/rpmbuild"}
spec_source="$repo_dir/libcamera.spec"
spec_dest="$topdir/SPECS/libcamera.spec"
sources_dir="$topdir/SOURCES"

if [[ $EUID -eq 0 ]]; then
	printf 'error: run this build as an ordinary user, not root\n' >&2
	exit 1
fi

for file in \
	"$spec_source" \
	"$repo_dir"/patches/*.patch \
	"$repo_dir"/packaging/70-libcamera.rules \
	"$repo_dir"/packaging/qcam.desktop \
	"$repo_dir"/packaging/qcam.metainfo.xml; do
	if [[ ! -f $file ]]; then
		printf 'error: required repository input is missing: %s\n' "$file" >&2
		exit 1
	fi
done

mkdir -p -- "$topdir"/{BUILD,BUILDROOT,RPMS,SOURCES,SPECS,SRPMS,TMP}
install -m 0644 -- "$spec_source" "$spec_dest"
install -m 0644 -- "$repo_dir"/patches/*.patch "$sources_dir/"
install -m 0644 -- \
	"$repo_dir/packaging/70-libcamera.rules" \
	"$repo_dir/packaging/qcam.desktop" \
	"$repo_dir/packaging/qcam.metainfo.xml" \
	"$sources_dir/"

printf 'Obtaining Source0 declared by %s ...\n' "$spec_dest"
spectool -g -C "$sources_dir" "$spec_dest"

printf 'Building in %s ...\n' "$topdir"
rpmbuild \
	--define "_topdir $topdir" \
	--define "_tmppath $topdir/TMP" \
	-ba "$spec_dest"

printf '\nGenerated packages:\n'
find "$topdir/RPMS" "$topdir/SRPMS" -type f \
	\( -name '*.rpm' -o -name '*.src.rpm' \) -print | sort
