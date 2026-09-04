---
name: Bug report
about: Report a build, installation, or camera issue
title: ""
labels: ""
assignees: ""
---

Before posting, remove usernames, hostnames, serial numbers, and account data.

## Environment

- Laptop model:
- Fedora release:
- Kernel:
- Sensor / platform:
- Installed libcamera package versions:

## What happened

Describe the symptom and the camera application used.

## Reproduction

List exact steps.

## Logs

Include relevant, redacted output from `wpctl status` and:

```bash
journalctl --user -b | grep -Ei 'libcamera|ov08x40|ipa|camera'
```

## Checklist

- [ ] I reproduced this with the complete matching RPM set.
- [ ] I checked whether `ov08x40.yaml` was selected.
- [ ] I removed private machine information.

