# Hardware and environment

## Tested configuration

This patch set was tested on one HP Spectre x360 14 from the 2024 generation,
with an Intel Meteor Lake platform, Intel IPU6 camera stack, and OV08X40 image
sensor. The operating system was Fedora 44 and the Fedora package base was
`libcamera-0.7.1-1.fc44`.

No other laptop, OV08X40 module, firmware combination, distribution release, or
libcamera version is claimed to work.

## Collecting useful diagnostics

Run these commands before reporting results. Review their output and redact any
serial numbers, account names, hostnames, or other identifying data before
sharing it.

```bash
cat /etc/fedora-release
uname -r
rpm -q libcamera libcamera-ipa pipewire-plugin-libcamera intel-vsc-firmware
wpctl status
lsusb
lspci -nn
journalctl --user -b | grep -Ei 'libcamera|ov08x40|ipa|camera'
```

Also note the laptop's exact model, whether Secure Boot is enabled, the camera
application used, and whether the problem reproduces in more than one
application. `lsusb` may not list an IPU6-connected sensor as a conventional USB
webcam; it remains useful for distinguishing other cameras.

