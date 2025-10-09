# proxy module to re-export the dashboard component from the original hyphenated package
from importlib import import_module
_mod = import_module('reactpy-components.dashboard')
# Re-export Dashboard and any others the template expects
Dashboard = getattr(_mod, 'Dashboard')
# optional re-exports
DeviceCatalogue = getattr(_mod, 'DeviceCatalogue', None)
Sidebar = getattr(_mod, 'Sidebar', None)
