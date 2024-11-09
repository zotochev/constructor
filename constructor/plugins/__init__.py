import importlib
from pathlib import Path

for p in Path(__file__).parent.iterdir():
	if not p.is_dir() or p.name.startswith('_'):
		continue
	importlib.import_module(f'plugins.{p.name}')

from .register import plugins_all
