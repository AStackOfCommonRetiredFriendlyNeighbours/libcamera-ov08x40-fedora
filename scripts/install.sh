#!/usr/bin/env bash
set -euo pipefail

for command in rpm dnf sudo find sort; do
	if ! command -v "$command" >/dev/null 2>&1; then
		printf 'error: required command not found: %s\n' "$command" >&2
		exit 1
	fi
done

if [[ $EUID -eq 0 ]]; then
	printf 'error: run this script as an ordinary user; it uses sudo only after confirmation\n' >&2
	exit 1
fi

topdir=${RPMBUILD_ROOT:-"${HOME:?HOME is not set}/rpmbuild"}
rpms_dir=${1:-"$topdir/RPMS"}

if [[ ! -d $rpms_dir ]]; then
	printf 'error: RPM directory not found: %s\n' "$rpms_dir" >&2
	printf 'Build first with scripts/build.sh, or pass an RPM directory.\n' >&2
	exit 1
fi

declare -A installed=()
while IFS=$'\t' read -r name arch; do
	[[ -n $name && -n $arch ]] && installed["$name.$arch"]=1
done < <(
	rpm -qa --qf $'%{NAME}\t%{ARCH}\n' |
		awk '$1 == "libcamera" || $1 ~ /^libcamera-/ || $1 == "python3-libcamera"'
)

if (( ${#installed[@]} == 0 )); then
	printf 'error: no installed libcamera packages were found\n' >&2
	exit 1
fi

declare -A selected_by_key=()
while IFS= read -r rpm_file; do
	read -r name arch < <(rpm -qp --qf '%{NAME} %{ARCH}\n' "$rpm_file")
	case $name in
		*-debuginfo|*-debugsource) continue ;;
	esac
	[[ $name == libcamera || $name == libcamera-* || $name == python3-libcamera ]] || continue

	key="$name.$arch"
	[[ -v installed[$key] ]] || continue
	if [[ -v selected_by_key[$key] ]]; then
		printf 'error: multiple candidate RPMs for %s:\n  %s\n  %s\n' \
			"$key" "${selected_by_key[$key]}" "$rpm_file" >&2
		printf 'Clean old RPM output or pass a directory containing one build.\n' >&2
		exit 1
	fi
	selected_by_key[$key]=$rpm_file
done < <(find "$rpms_dir" -type f -name '*.rpm' ! -name '*.src.rpm' -print | sort)

if (( ${#selected_by_key[@]} == 0 )); then
	printf 'error: no built RPM corresponds to an installed libcamera subpackage\n' >&2
	exit 1
fi

mapfile -t selected < <(printf '%s\n' "${selected_by_key[@]}" | sort)

printf 'libcamera subpackages have exact-version dependencies. The following\n'
printf 'matching installed subpackages must be upgraded as one transaction:\n'
printf '  %s\n' "${selected[@]}"

printf '\nDNF transaction preview (no changes will be made):\n'
set +e
dnf install --assumeno -- "${selected[@]}"
preview_status=$?
set -e
if (( preview_status != 0 && preview_status != 1 )); then
	printf 'error: DNF could not produce a transaction preview (status %d)\n' \
		"$preview_status" >&2
	exit "$preview_status"
fi

printf '\nProceed with exactly this local RPM set? [y/N] '
read -r answer
case $answer in
	y|Y|yes|YES|Yes) ;;
	*) printf 'Installation cancelled.\n'; exit 0 ;;
esac

sudo dnf install -- "${selected[@]}"

