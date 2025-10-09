# compatibility wrapper package for files originally under reactpy-components
# This package re-exports the modules so they can be imported using a
# Python module name without hyphens (used by reactpy_django component loader).
from importlib import import_module

# Import and expose the dashboard module
_dashboard = import_module('reactpy-components.dashboard')
Dashboard = getattr(_dashboard, 'Dashboard', None)
# Re-export any others lazily as needed
