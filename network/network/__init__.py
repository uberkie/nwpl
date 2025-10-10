"""Project package initialisation.

Expose sibling app packages (e.g. ``planning`` and ``reactpy_components``)
under the ``network`` namespace so dotted imports such as
``network.planning`` continue to work regardless of the current working
directory used to launch Django management commands.
"""

from importlib import import_module
import sys


def _alias_sibling(package_name: str) -> None:
	"""Import *package_name* and register it as ``network.<package_name>``."""

	try:
		module = import_module(package_name)
	except ModuleNotFoundError:
		return

	sys.modules.setdefault(f"{__name__}.{package_name}", module)
	setattr(sys.modules[__name__], package_name, module)


for _pkg in ("planning", "reactpy_components"):
	_alias_sibling(_pkg)

del _alias_sibling, import_module, sys
