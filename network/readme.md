# Next Level Networks – Network Planning Tool

An interactive, server-driven network planning dashboard built with Django and ReactPy. The app lets you drag-and-drop devices onto a canvas, stitch links between ports, edit properties in-place, and validate connectivity with an embedded network simulator – all without client-side JavaScript.

## 🚀 Features at a Glance

- **Drag-and-drop topology builder** – position routers, switches, servers, terminals, and more on an SVG canvas.
- **ORM-backed device catalogue** – manage reusable device models in the database; the ReactPy catalogue stays in sync automatically.
- **Rich port & bridge editor** – rename interfaces, assign VLANs, move ports into bridges, and add/remove interfaces on the fly.
- **Link management** – create, color, and annotate links; compatibility checks ensure only valid interface types connect.
- **Export / Import** – snapshot the current topology to JSON or reload prior designs.
- **Embedded simulator terminal** – run `ping` and `traceroute` commands against the live topology using the lightweight network simulator (supports NAT, routing tables, and bridges).
- **Admin tooling** – manage device catalogue entries via the dedicated ReactPy admin component or the Django admin site.

## 🧰 Prerequisites

- Python 3.12+
- SQLite (bundled) or another Django-supported database if you plan to swap backends
- Node.js **NOT** required (ReactPy renders server-side)

Recommended additional services and packages (used by the development server and Channels):

- Redis (for Django Channels channel layer)
- Daphne (ASGI server) and Channels (Django Channels package)

Quick install and verification (Linux / macOS):

- Install Redis (Debian/Ubuntu):

```bash
sudo apt update
sudo apt install -y redis-server
sudo systemctl enable --now redis.service
redis-cli ping  # should reply PONG
```

- Install Redis (macOS via Homebrew):

```bash
brew update
brew install redis
brew services start redis
redis-cli ping
```

- Install Daphne and Channels inside your Python virtualenv:

```bash
pip install daphne channels channels_redis
```

- (Optional) Run the development server with Daphne instead of Django's runserver:

```bash
# Example: run daphne on port 8000
daphne -b 127.0.0.1 -p 8000 network.asgi:application
```

Docker option (quick local redis + daphne):

```bash
# Start Redis with Docker
docker run -d --name redis -p 6379:6379 redis:7-alpine

# Run Daphne in your container or locally pointed at Redis inside the docker network
```

## 🔧 Setup & Basic Usage

1. **Clone & create a virtual environment**
	```bash
	git clone <repo-url>
	cd nwpl/network
	python3 -m venv .venv
	source .venv/bin/activate
	```

2. **Install dependencies**
	```bash
	pip install -r requirements.txt
	```

3. **Apply database migrations**
	```bash
	python manage.py migrate
	```

4. **(Optional but Recommended) Update ReactPy SVG constructors**  
	ReactPy currently requires a small tweak so SVG `<text>`/`<title>` nodes accept children:
	```python
	# site-packages/reactpy/svg.py
	# patch_reactpy_svg.py
	import re
	import pathlib
	
	path = pathlib.Path(__file__).parent / "venv/lib/python3.10/site-packages/reactpy/svg.py"
	text = path.read_text()
	
	# Example: change allow_children=False -> True
	text = re.sub(r'("text".*?allow_children=)False', r'\1True', text)
	text = re.sub(r'("title".*?allow_children=)False', r'\1True', text)
	
	path.write_text(text)
	print("✅ reactpy/svg.py patched successfully.")
	```

5. **Run the development server**
	```bash
	python manage.py runserver
	```

6. **Open the dashboard**  
	Visit http://127.0.0.1:8000/ to launch the planning UI.

### Working with the Dashboard

- **Add devices** from the sidebar catalogue, then rename and position them directly on the canvas.
- **Connect ports** by toggling “Add Link”, clicking two ports, and selecting a compatible link type.
- **Edit bridges, VPNs, tunnels, and ports** using the properties panel on the right.
- **Simulator Terminal**: Expand the “Simulator Terminal” drawer, choose a device & port, then issue commands like `ping 192.0.2.2 203.0.113.5` or `traceroute 192.0.2.2 8.8.8.8`. The simulator rebuilds itself from the current canvas state, so tests run against your live topology.
- **Export / Import**: Use the footer toggle to copy JSON snapshots or paste existing designs.

## ✅ Current Capabilities

- Device catalogue CRUD (ReactPy admin component + Django ORM)
- Canvas layout with drag, select, delete
- Port/bridge/VLAN editing and automatic normalization of legacy exports
- Link creation with context menu editing (color, notes, IPs)
- JSON export/import
- Real-time simulator terminal (ping & traceroute) powered by the in-project `NetworkSimulator`
- Basic NAT and routing support within the simulator (SNAT/DNAT, longest-prefix routing, bridge learning)

7. **Running Production**
-  Create the following file to run daphne as a service

	```bash
	sudo nano /etc/systemd/system/myproject.daphne.service
	[Unit]
	Description=daphne daemon for my project
	After=network.target

	[Service]
	User=aj
	WorkingDirectory=/path/to/project
	ExecStart=/path/to/project/.venv/bin/daphne -b 0.0.0.0 -p 8000 network.asgi:application
	Restart=on-failure

	[Install]
	WantedBy=multi-user.target
	```

## 🛣️ Toward Production Readiness (Todo List)

- [ ] Persist diagram states per user/project instead of in-memory ReactPy state
- [ ] Add authentication & authorization around catalogue edits and topology access
- [ ] Implement server-side validation & APIs for saving/loading schematics
- [ ] Comprehensive test suite (unit + integration for simulator, ReactPy components, and Django views)
- [ ] CI pipeline (lint, tests, type checks) and deployment scripts
- [ ] Real-time collaboration / locking for multi-user editing sessions
- [ ] Accessible UI pass (keyboard navigation, ARIA roles, contrast checks)
- [ ] Error handling & user feedback for simulator failures and form validation
- [ ] Configuration UI for custom device icons, vendor metadata, and link templates
- [ ] Documentation site with tutorials, architecture diagrams, and simulator reference

## 🤝 Contributing

Issues and pull requests are welcome! Please include tests for functional changes and keep the README updated as features evolve.

---

*Next Level Networks – plan, simulate, and validate complex topologies entirely server-side.*