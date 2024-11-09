import importlib
from pathlib import Path

from .plugin import APlugin
from .register import plugins_all

for p in Path(__file__).parent.iterdir():
	if not p.is_dir() or p.name.startswith('_'):
		continue
	a = importlib.import_module(f'plugins.{p.name}')
	for k, v in a.__dict__.items():
		if (isinstance(v, type)
			and issubclass(v, APlugin)
			and v is not APlugin
			and v not in plugins_all):
			plugins_all.append(v)

plugins_all.sort(key=lambda x: x.order)
