# Rollback

Close camera applications before rollback. The custom libcamera subpackages use
exact-version dependencies, so restore the installed package set together.

First inspect installed custom builds:

```bash
rpm -qa --qf '%{NAME} %{EVR}.%{ARCH}\n' | grep -E '^(libcamera|python3-libcamera) '
```

With the normal Fedora repositories enabled, synchronize those packages back to
the repository versions:

```bash
sudo dnf distro-sync --refresh 'libcamera*' 'python3-libcamera'
```

Review the transaction carefully before confirming. If version locking or an
excluded package prevents the operation, inspect those settings first:

```bash
sudo dnf versionlock list
dnf repoquery --installed 'libcamera*' 'python3-libcamera'
dnf repoquery --latest-limit 1 'libcamera*' 'python3-libcamera'
```

If `versionlock` is unavailable, that diagnostic can simply be skipped. Do not
use `rpm --force` or remove the core library while exact-version dependants are
installed. Restart camera applications (or log out and back in) after rollback.

Fedora updates may provide a newer libcamera that supersedes both the official
0.7.1 build and this patch set. `distro-sync` intentionally uses current enabled
repositories instead of hard-coding a version that will become stale.

