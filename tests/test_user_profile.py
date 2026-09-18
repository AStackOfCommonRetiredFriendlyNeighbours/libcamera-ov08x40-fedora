# SPDX-License-Identifier: MIT
# Isolated installer checks; systemd calls are mocked.
import importlib.util
import os
from pathlib import Path
import tempfile
from unittest.mock import patch
import yaml

spec=importlib.util.spec_from_file_location('installer',str(Path(__file__).resolve().parents[1] / 'scripts/install-user-fix.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
with tempfile.TemporaryDirectory() as directory:
 root=Path(directory); cfg=root/'config'; state=root/'state'; settings=cfg/'libcamera/configuration.yaml'
 settings.parent.mkdir(parents=True)
 original='version: 1\nconfiguration:\n  software_isp:\n    threads: 4\n  ipa:\n    config_paths: [/existing]\n'
 settings.write_text(original)
 with patch.dict(os.environ,{'XDG_CONFIG_HOME':str(cfg),'XDG_STATE_HOME':str(state)}), patch.object(m.Path,'home',return_value=root), patch.object(m.os,'geteuid',return_value=1000), patch.object(m.shutil,'which',return_value='/usr/bin/stub'), patch.object(m.subprocess,'run') as run:
  with patch('sys.argv',['installer','--dry-run']): m.main()
  assert not state.exists() and settings.read_text()==original and not run.called
  with patch('sys.argv',['installer']): m.main()
  data=yaml.safe_load(settings.read_text())
  assert data['configuration']['software_isp']['threads']==4
  assert data['configuration']['ipa']['config_paths']==[str(cfg/'libcamera/ipa'),'/existing']
  backups=list((state/'ov08x40-fix/backups').iterdir())
  assert len(backups)==1 and (backups[0]/'configuration.yaml').read_text()==original
  assert (root/'.local/libexec/ov08x40-gain').stat().st_mode & 0o111
  assert yaml.safe_load((cfg/'libcamera/ipa/simple/ov08x40.yaml').read_text())['algorithms'][-1]['Agc']['maxAnalogueGain']==3.0
  with patch('sys.argv',['installer']): m.main()
  assert len(list((state/'ov08x40-fix/backups').iterdir()))==2
  assert yaml.safe_load(settings.read_text())['configuration']['ipa']['config_paths'].count(str(cfg/'libcamera/ipa'))==1
  settings.unlink();settings.symlink_to(backups[0]/'configuration.yaml')
  try:
   with patch('sys.argv',['installer']):m.main()
  except SystemExit as e: assert 'symlink' in str(e)
  else: raise AssertionError('symlink accepted')
print('PASS: dry-run, config merge, exact backup, permissions, final tuning, repeat install, symlink protection; services mocked.')
