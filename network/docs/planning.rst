Planning Django App
===================

The :mod:`planning` package contains the Django app that powers the network
planning dashboard. It wires together ReactPy components, database-backed device
catalogues, and the server-driven routing layer exposed at ``/``.

High-level responsibilities
---------------------------

* Serve the ReactPy dashboard via :func:`planning.views.dashboard_view`.
* Provide simple JSON endpoints (e.g. ``/add_device/``) for catalogue updates.
* Persist available device models with :class:`planning.models.DeviceModel`.
* Relay simulator updates to connected clients via Channels consumers.
* Surface admin tooling and signal hooks for catalogue change notifications.

Data model
----------

``DeviceModel`` encapsulates reusable device catalogue entries. Fields include:

=================  ===========================================================
Field              Description
=================  ===========================================================
``category``       Logical grouping (e.g. ``Router``, ``Switch``, ``Server``).
``type``           Device type used by ReactPy when seeding UI defaults.
``model``          Vendor/model identifier or internal SKU.
``ports``          Number of default interfaces exposed in the dashboard.
``display``        Human-readable label shown in the catalogue.
``created_at``     Timestamp automatically managed by Django.
``updated_at``     Timestamp automatically managed by Django.
=================  ===========================================================

View layer
----------

* :func:`planning.views.dashboard_view` mounts the ReactPy dashboard and ensures
  catalogue seeding on first run.
* :func:`planning.views.add_device` provides a lightweight JSON endpoint for
  creating new catalogue entries (used by the ReactPy admin component).

Real-time integration
---------------------

``planning.consumers`` exposes Channels consumers that broadcast catalogue
changes. Paired with the ``reactpy_components._notifier`` helper they ensure the
ReactPy catalogue updates across browser sessions without a full page refresh.

Signals
-------

``planning.signals`` listens for :class:`planning.models.DeviceModel` saves and
deletions. Whenever a catalogue record changes, the signal emits a notification
that wakes the in-process ReactPy dashboard and any subscribed Channels
listeners.

Testing
-------

Unit tests live in :mod:`planning.tests` and cover view responses, model
behaviour, and regression scenarios for the simulator integration points. Use
``python manage.py test planning`` during development.

Subpackages
-----------

.. toctree::
   :maxdepth: 3

   api



API Reference
-------------

.. automodule:: planning
   :members:
   :show-inheritance:
   :undoc-members:

.. automodule:: planning.admin
   :members:
   :show-inheritance:
   :undoc-members:

.. automodule:: planning.apps
   :members:
   :show-inheritance:
   :undoc-members:

.. automodule:: planning.consumers
   :members:
   :show-inheritance:
   :undoc-members:

.. automodule:: planning.models
   :members:
   :show-inheritance:
   :undoc-members:

.. automodule:: planning.routing
   :members:
   :show-inheritance:
   :undoc-members:

.. automodule:: planning.signals
   :members:
   :show-inheritance:
   :undoc-members:

.. automodule:: planning.tests
   :members:
   :show-inheritance:
   :undoc-members:

.. automodule:: planning.urls
   :members:
   :show-inheritance:
   :undoc-members:

.. automodule:: planning.views
   :members:
   :show-inheritance:
   :undoc-members:
