#!/usr/bin/python3
# SPDX-License-Identifier: MIT
"""Install the local OV08X40 profile, preserving unrelated libcamera settings."""
import argparse
from datetime import datetime
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import sys

import yaml


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dry-run', action='store_true', help='validate and show changes without writing or restarting services')
    args = parser.parse_args()
    if os.geteuid() == 0:
        sys.exit('Run as your desktop user, not with sudo.')
    for command in ('v4l2-ctl', 'systemctl'):
        if not shutil.which(command):
            sys.exit(f'Missing {command}; see docs/reproduce-results.md.')
    repo = Path(__file__).resolve().parent.parent
    config = Path(os.environ.get('XDG_CONFIG_HOME') or Path.home() / '.config')
    state = Path(os.environ.get('XDG_STATE_HOME') or Path.home() / '.local/state')
    if not config.is_absolute() or not state.is_absolute():
        sys.exit('XDG_CONFIG_HOME and XDG_STATE_HOME must be absolute paths.')
    settings = config / 'libcamera/configuration.yaml'
    data = yaml.safe_load(settings.read_text()) if settings.exists() else {}
    data = data or {}
    if not isinstance(data, dict) or data.get('version', 1) != 1:
        sys.exit('Unsupported libcamera configuration; merge the profile manually.')
    data['version'] = 1
    configuration = data.setdefault('configuration', {})
    if not isinstance(configuration, dict):
        sys.exit('configuration must be a mapping.')
    ipa = configuration.setdefault('ipa', {})
    if not isinstance(ipa, dict):
        sys.exit('ipa must be a mapping.')
    paths = ipa.get('config_paths', [])
    if not isinstance(paths, list) or not all(isinstance(p, str) for p in paths):
        sys.exit('ipa.config_paths must be a list of paths.')
    tuning_dir = str(config / 'libcamera/ipa')
    ipa['config_paths'] = [tuning_dir] + [p for p in paths if p != tuning_dir]
    changes = {
        settings: (yaml.safe_dump(data, sort_keys=False).encode(), 0o644),
        config / 'libcamera/ipa/simple/ov08x40.yaml': ((repo / 'config/ov08x40.yaml').read_bytes(), 0o644),
        Path.home() / '.local/libexec/ov08x40-gain': ((repo / 'scripts/ov08x40-gain').read_bytes(), 0o755),
        config / 'systemd/user/ov08x40-gain.service': ((repo / 'systemd/ov08x40-gain.service').read_bytes(), 0o644),
    }
    for target in changes:
        if target.is_symlink() or (target.exists() and not target.is_file()):
            sys.exit(f'Refusing to replace symlink or non-file: {target}')
        print(f'Install: {target}')
    print('Enable/restart ov08x40-gain.service and restart WirePlumber (brief audio/video interruption).')
    if args.dry_run:
        return
    subprocess.run(['systemctl', '--user', 'show-environment'], check=True, stdout=subprocess.DEVNULL)
    backup_root = state / 'ov08x40-fix/backups'
    backup_root.mkdir(parents=True, exist_ok=True)
    backup = Path(tempfile.mkdtemp(prefix=datetime.now().strftime('%Y%m%d-%H%M%S-'), dir=backup_root))
    manifest = []
    for target in changes:
        existed = target.exists()
        if existed:
            shutil.copy2(target, backup / target.name)
        manifest.append({'path': str(target), 'existed': existed, 'backup': target.name})
    (backup / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(f'Backup: {backup}', flush=True)
    for target, (content, mode) in changes.items():
        target.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(dir=target.parent, delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(content)
        temporary.chmod(mode)
        temporary.replace(target)
    subprocess.run(['systemctl', '--user', 'daemon-reload'], check=True)
    subprocess.run(['systemctl', '--user', 'enable', 'ov08x40-gain.service'], check=True)
    subprocess.run(['systemctl', '--user', 'restart', 'ov08x40-gain.service'], check=True)
    subprocess.run(['systemctl', '--user', 'restart', 'wireplumber.service'], check=True)
    print('Installed. Reopen camera apps. See docs/reproduce-results.md for verification and rollback.')


if __name__ == '__main__':
    main()
