.. Next Level Networks – Network Planning Tool documentation master file, created by
   sphinx-quickstart on Fri Oct 10 12:57:37 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Next Level Networks – Network Planning Tool
==========================================

An interactive, server-driven network planning environment built with Django and
ReactPy. The application lets engineers design topologies, manage device
catalogues, edit bridges and VLANs, and validate connectivity using an embedded
Python network simulator – all without shipping browser-side JavaScript.

Overview
--------

``Next Level Networks`` combines three major building blocks:

* **ReactPy dashboard** – a draggable SVG canvas with device catalogue,
   properties panel, link controls, and an in-app terminal.
* **Django backend** – persistence for device models, REST-style endpoints for
   topology operations, and admin tooling.
* **Lightweight simulator** – models routers, bridges, NAT, and ICMP to sanity
   check paths directly from the dashboard UI.

Key Features
------------

* Drag-and-drop device placement on a zoom-friendly canvas.
* ORM-backed device catalogue with ReactPy CRUD admin.
* Per-port editing: names, interface types, IP assignments, VLANs, bridge
   membership, and ad-hoc interface creation/removal.
* Link management with compatibility checks, color coding, comments, and JSON
   export/import support.
* Embedded simulator terminal supporting ``ping`` and ``traceroute`` against
   the live topology, plus NAT-aware routing logic.
* Automatic normalisation of legacy exports (port IDs, bridge membership).

Quick Start
-----------

1. **Install dependencies**::

          python3 -m venv .venv
          source .venv/bin/activate
          pip install -r requirements.txt

2. **Apply database migrations**::

          python manage.py migrate

3. **(Optional) Patch ReactPy SVG constructors** – enable text/title children by
    editing ``site-packages/reactpy/svg.py``::

          text = make_vdom_constructor("text", allow_children=True)
          title = make_vdom_constructor("title", allow_children=True)

4. **Run the development server**::

          python manage.py runserver

5. Open http://127.0.0.1:8000/ to launch the dashboard.

Dashboard Tour
--------------

* **Device Catalogue** – organise hardware by category, seeded from the Django
   ORM. Add devices with unique names, then drag them onto the canvas.
* **Canvas Interactions** – drag to reposition, select to reveal properties,
   and open the context menu on links for colour and comment edits.
* **Properties Panel** – modify ports, bridges, VPNs, and IP tunnels; add or
   remove interfaces; assign VLANs; and invoke manual link creation.
* **Simulator Terminal** – choose a device and port, then run ``ping`` or
   ``traceroute``. The simulator rebuilds from the current canvas state so
   results always reflect the live topology.
* **Export / Import** – generate JSON snapshots or reload prior designs for
   iteration and sharing.

Current Capabilities
--------------------

* Device catalogue CRUD via ReactPy and Django admin.
* Canvas layout with draggable devices, deletions, and link context editing.
* Automatic port/bridge/VLAN normalisation for backwards-compatible imports.
* Simulator support for bridges, routers, SNAT/DNAT, and longest-prefix routing.
* Real-time feedback from simulator commands embedded within the dashboard.

Production Hardening Checklist
-------------------------------

* [ ] Persist user-specific diagrams (database or revisioned storage).
* [ ] Add authentication/authorization guardrails around catalogue & topology
   access.
* [ ] Provide APIs for saving/loading schematics and integrating with external
   tooling.
* [ ] Expand automated testing: Django views, simulator unit tests, and
   ReactPy component snapshots.
* [ ] Introduce CI/CD pipeline with linting, type checks, and deployment
   automation.
* [ ] Improve accessibility (keyboard navigation, ARIA roles, colour contrast).
* [ ] Harden simulator error handling and expose structured diagnostics in UI.
* [ ] Document architecture, simulator internals, and extension workflows.

Further Reading
---------------

* `ReactPy documentation <https://reactpy.dev/>`_
* `Django documentation <https://docs.djangoproject.com/en/stable/>`_
* `Sphinx reStructuredText essentials <https://www.sphinx-doc.org/en/master/usage/restructuredtext/index.html>`_

.. toctree::
    :maxdepth: 2
    :caption: API Reference

    modules


