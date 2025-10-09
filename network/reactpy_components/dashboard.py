from reactpy import component, html, svg, hooks, use_state, event
from reactpy_components.device_catalogue import DEVICE_CATALOGUE
import asyncio

@component
def Sidebar(on_add_device=None, on_toggle_link=None, linking_active=False, catalogue=None):
    # Sidebar now accepts callbacks from Dashboard so actions are server-driven
    # link filter state (controlled checkboxes)
    link_types = [
        "Ethernet",
        "DAC",
        "AOC",
        "Fibre",
        "Wireless",
        "VPN",
        "VLAN",
        "IP-IP Tunnel",
        "IP Sec Tunnel",
        "Routed",
    ]
    default_filters = {t: True for t in link_types}
    link_filters, set_link_filters = use_state(default_filters)

    def _toggle_filter(t, checked):
        set_link_filters({**link_filters, t: checked})

    def _checked_from_event(e):
        try:
            tgt = e.get('target') if isinstance(e, dict) else None
            if isinstance(tgt, dict) and 'checked' in tgt:
                return tgt.get('checked')
            # fallbacks
            return bool(e.get('checked', False)) if isinstance(e, dict) else False
        except Exception:
            return False

    return html.div(
        {"className": "sidebar", "style": {"overflowY": "auto", "maxHeight": "100vh"}},  # Added scroll

        html.div({"className": "toolbar"},
                 html.h3({}, "Device Catalogue"),
                 html.div({"className": "device-catalogue"}, DeviceCatalogue(catalogue, on_add_device)),
                 html.hr(),
                 html.h3({}, "Device Filters"),
                 html.div({"id": "device-filter-group", "className": "filter-group"}),
                 html.h3({}, "Link Filters"),
                 html.div({"id": "link-filter-group", "className": "filter-group"},
                          html.label({},
                                     html.input({
                                         "type": "checkbox",
                                         "data-link-type": "Ethernet",
                                         "checked": link_filters.get("Ethernet", True),
                                         "on_change": lambda e: _toggle_filter("Ethernet", _checked_from_event(e))
                                     }),
                                     " Ethernet"),
                          html.label({}, html.input({
                              "type": "checkbox",
                              "data-link-type": "DAC",
                              "checked": link_filters.get("DAC", True),
                              "on_change": lambda e: _toggle_filter("DAC", _checked_from_event(e))
                          }),
                                     " DAC"),
                          html.label({}, html.input({
                              "type": "checkbox",
                              "data-link-type": "AOC",
                              "checked": link_filters.get("AOC", True),
                              "on_change": lambda e: _toggle_filter("AOC", _checked_from_event(e))
                          }),
                                     " AOC"),
                          html.label({}, html.input({
                              "type": "checkbox",
                              "data-link-type": "Fibre",
                              "checked": link_filters.get("Fibre", True),
                              "on_change": lambda e: _toggle_filter("Fibre", _checked_from_event(e))
                          }),
                                     " Fibre"),
                          html.label({
                                     },
                                     html.input({
                                         "type": "checkbox",
                                         "data-link-type": "Wireless",
                                         "checked": link_filters.get("Wireless", True),
                                         "on_change": lambda e: _toggle_filter("Wireless", _checked_from_event(e))
                                     }),
                                     " Wireless"),
                          html.label({}, html.input({
                              "type": "checkbox",
                              "data-link-type": "VPN",
                              "checked": link_filters.get("VPN", True),
                              "on_change": lambda e: _toggle_filter("VPN", _checked_from_event(e))
                          }),
                                     " VPN"),
                          html.label({}, html.input({
                              "type": "checkbox",
                              "data-link-type": "VLAN",
                              "checked": link_filters.get("VLAN", True),
                              "on_change": lambda e: _toggle_filter("VLAN", _checked_from_event(e))
                          }),
                                     " VLAN"),
                          html.label({}, html.input(
                              {"type": "checkbox", "data-link-type": "IP-IP Tunnel", "checked": link_filters.get("IP-IP Tunnel", True),
                               "on_change": lambda e: _toggle_filter("IP-IP Tunnel", _checked_from_event(e))}),
                                     " IP-IP Tunnel"),
                          html.label({}, html.input(
                              {"type": "checkbox", "data-link-type": "IP Sec Tunnel", "checked": link_filters.get("IP Sec Tunnel", True),
                               "on_change": lambda e: _toggle_filter("IP Sec Tunnel", _checked_from_event(e))}),
                                     " IP Sec Tunnel"),
                          html.label({}, html.input({
                              "type": "checkbox",
                              "data-link-type": "Routed",
                              "checked": link_filters.get("Routed", True),
                              "on_change": lambda e: _toggle_filter("Routed", _checked_from_event(e))
                          }),
                                     " Routed")),
                 html.h3({}, "Actions"),
                 html.button({"id": "add-link-btn", "className": "toolbar-button",
                              "onClick": (lambda e: on_toggle_link() if on_toggle_link else None)}, "🔗 Add Link"),
                 html.button({"id": "export-jpg-btn", "className": "toolbar-button"}, "🖼️ Export as JPG"),
                 html.button({"id": "export-json-btn", "className": "toolbar-button"}, "📤 Export Schematic"),
                 html.label({"htmlFor": "import-file", "id": "import-btn", "className": "toolbar-button"},
                            "📥 Import Schematic"),
                 html.input({"type": "file", "id": "import-file", "accept": ".json", "style": {"display": "none"}}),
                 html.button({"id": "new-schematic-btn", "className": "toolbar-button"}, "📄 New Schematic")))





@component
def CatalogueItem(device, on_add_device=None):
    name, set_name = use_state("")

    def add_device(e):
        if on_add_device:
            on_add_device({**device, "name": name})
            set_name("")

    return html.div({"className": "catalogue-item", "data-type": device["type"], "data-model": device["model"],
                     "data-ports": device["ports"]},
                    html.p(device["display"]),
                    html.div({"className": "controls"},
                             html.input({"type": "text", "placeholder": "Device Name", "value": name,
                                         "on_change": lambda e: set_name(e['target']['value'])}),
                             html.button({"className": "add-device-btn", "onClick": add_device}, "+")))


@component
def DeviceCategory(category_name, devices, on_add_device=None):
    return html.details({"open": True},
                        html.summary(category_name),
                        *[CatalogueItem(device, on_add_device) for device in devices])


@component
def DeviceCatalogue(catalogue=None, on_add_device=None):
        # catalogue is expected to be a mapping: category -> list of device dicts
        data = catalogue or DEVICE_CATALOGUE
        return html.div({"className": "device-catalogue"},
                                        *[DeviceCategory(category_name, devices, on_add_device) for category_name, devices in
                                            (data.items() if isinstance(data, dict) else [] )])


@component
def ThemeSwitcher(children):
    return html.div({"className": "theme-wrapper"}, children)


from reactpy import component, html, hooks, use_state


@component
def PortItem(port, device_id, on_update_port=None, on_remove_port=None, on_add_port=None, on_update_bridge=None, bridges=None):
    from reactpy import html

    # Local state for this port
    name, set_name = use_state(port.get("name", ""))
    ips, set_ips = use_state(list(port.get("ips", [])))
    vlans, set_vlans = use_state(list(port.get("vlans", [])))
    bridge, set_bridge = use_state(port.get("bridge", ""))
    iftype, set_iftype = use_state(port.get("iftype", "ethernet"))
    ip_input, set_ip_input = use_state("")
    vlan_input, set_vlan_input = use_state("")
    is_open, set_open = use_state("False")

    # keep local state in sync when the parent updates the port prop
    def _sync_port():
        set_name(port.get("name", ""))
        set_ips(list(port.get("ips", [])))
        set_vlans(list(port.get("vlans", [])))
        set_bridge(port.get("bridge", ""))
        set_iftype(port.get("iftype", "ethernet"))
        # no cleanup function
        return None

    hooks.use_effect(_sync_port, [port])

    # Handlers
    def handle_name_change(e):
        set_name(e['target']['value'])
        if on_update_port:
            on_update_port(port['id'], {"name": e['target']['value']})

    def handle_bridge_change(e):
        set_bridge(e['target']['value'])
        if on_update_port:
            on_update_port(port['id'], {"bridge": e['target']['value']})

    def handle_iftype_change(e):
        val = e['target']['value']
        set_iftype(val)
        if on_update_port:
            on_update_port(port['id'], {"iftype": val})

    def add_ip(ip_value):
        if ip_value:
            new_ips = ips + [ip_value]
            set_ips(new_ips)
            if on_update_port:
                on_update_port(port['id'], {"ips": new_ips})

    def add_vlan(vlan_value):
        if vlan_value:
            new_vlans = vlans + [vlan_value]
            set_vlans(new_vlans)
            # If this port is part of a bridge, apply VLANs to the bridge (interface) instead
            if port.get('bridge') and on_update_bridge:
                on_update_bridge(device_id, port.get('bridge'), {"vlans": new_vlans})
            elif on_update_port:
                on_update_port(port['id'], {"vlans": new_vlans})

    def remove_port(event):
        if on_remove_port:
            on_remove_port(port['id'])

    def add_port_click(event):
        if on_add_port:
            on_add_port(device_id)

    def handle_open(event):
        set_open(event)

    # Render
    return html.div({"className": "prop-group"},
                    html.label({}, "Ports"),
                    html.ul({},
                            html.details({"open": False},
                                         html.summary({"className": "port-header"}, name),

                                    html.div({"className": "port-details"},
                                             html.label({}, "Name"),
                                             html.input({
                                                 "type": "text",
                                                 "className": "port-name-input",
                                                 "value": name,
                                                 "on_change": handle_name_change
                                             }),
                                             html.label({}, "Bridge Assignment"),
                                             html.select({
                                                 "className": "port-bridge-select",
                                                 "value": bridge,
                                                 "on_change": handle_bridge_change
                                             },
                                                 html.option({"value": ""}, "(None)"),
                                                 *[html.option({"value": b["id"]}, b.get("name", b.get("id"))) for b in (bridges or [])]
                                             ),
                                             html.label({}, "Interface Type"),
                                             html.select({
                                                 "className": "port-iftype-select",
                                                 "value": iftype,
                                                 "on_change": handle_iftype_change
                                             },
                                                 html.option({"value": "ethernet"}, "Ethernet"),
                                                 html.option({"value": "wireless"}, "Wireless"),
                                                html.option({"value": "fibre"}, "Fibre"),
                                                html.option({"value": "virtual-wireless"}, "Virtual Wireless")
                                             ),
                                             html.hr({"style": {"borderColor": "#444"}}),
                                             html.label({}, "IP Addresses (Untagged)"),
                                             html.div({"className": "port-ip-list"}, *[
                                                 html.div({}, ip, html.button({
                                                     "className": "small",
                                                     "style": {"marginLeft": "8px"},
                                                     "on_click": (lambda e, ip_addr=ip: (set_ips([x for x in ips if x != ip_addr]), on_update_port and on_update_port(port['id'], {"ips": [x for x in ips if x != ip_addr]})))
                                                 }, "Remove"))
                                                 for ip in ips
                                             ]),
                                             html.input({
                                                 "type": "text",
                                                 "placeholder": "Add IP/Mask",
                                                 "value": ip_input,
                                                 "on_change": lambda e: set_ip_input(e['target']['value'])
                                             }),
                                             html.button({
                                                 "className": "prop-button small info add-ip-btn",
                                                 "onClick": lambda e: add_ip(ip_input) or set_ip_input("")
                                             }, "Add IP"),
                                             html.label({"style": {"marginTop": "10px"}}, "VLANs"),
                                             html.div({"className": "port-vlan-list"},
                                                      *[html.div({}, v) for v in vlans]),
                                             html.input({
                                                 "type": "number",
                                                 "placeholder": "Add VLAN ID",
                                                 "min": 1,
                                                 "max": 4094,
                                                 "value": vlan_input,
                                                 "on_change": lambda e: set_vlan_input(e['target']['value'])
                                             }),
                                             html.button({
                                                 "className": "prop-button small info add-vlan-btn",
                                                 "onClick": lambda e: add_vlan(vlan_input) or set_vlan_input("")
                                             }, "Add VLAN"),
                                             html.hr({"style": {"borderColor": "#444"}}),
                                             html.button({
                                                 "className": "prop-button danger remove-port-btn",
                                                 "onClick": remove_port
                                             }, "Remove Port")
                                             )
                                    )
                            ),
                    html.button({
                        "id": "add-port-btn",
                        "className": "prop-button",
                        "onClick": add_port_click
                    }, "Add Port")
                    )


@component
def ContextMenuExample():
    """Minimal example component that demonstrates ReactPy @event(prevent_default=True)
    to suppress the browser's default context menu and capture client coordinates.
    """
    show_menu, set_show_menu = hooks.use_state(False)
    pos, set_pos = hooks.use_state({"x": 0, "y": 0})

    @event(prevent_default=True, stop_propagation=True)
    def handle_contextmenu(e):
        x = e.get("clientX", 0)
        y = e.get("clientY", 0)
        set_pos({"x": int(x), "y": int(y)})
        set_show_menu(True)

    def handle_click(e):
        set_show_menu(False)

    return html.div({
        "onClick": handle_click,
        "style": {"height": "100vh", "background": "#f0f0f0", "position": "relative"},
    },
        html.div({
            "onContextMenu": handle_contextmenu,
            "style": {"color": "blue", "textDecoration": "underline", "cursor": "pointer"},
        }, "Right-click this 'link-like' text"),
        show_menu and html.ul({
            "style": {
                "position": "absolute",
                "top": f"{pos['y']}px",
                "left": f"{pos['x']}px",
                "background": "#222",
                "color": "#fff",
                "padding": "8px",
                "listStyle": "none",
                "border": "1px solid #444",
                "borderRadius": "4px",
                "zIndex": 1000,
            }
        }, html.li({}, "Edit"), html.li({}, "Delete"), html.li({}, "View Properties"))
    )

    # ---------------- Bridges Panel ----------------


@component
def BridgesPanel(bridges, on_add_bridge, on_update_bridge, on_remove_bridge):
    @component
    def BridgeItem(b):
        vlan_input, set_vlan_input = hooks.use_state("")

        def add_vlan(e=None):
            try:
                v = int(vlan_input)
            except Exception:
                return
            current = b.get('vlans', []) or []
            if v in current:
                set_vlan_input("")
                return
            on_update_bridge(b['id'], {'vlans': current + [v]})
            set_vlan_input("")

        def remove_vlan(v):
            current = b.get('vlans', []) or []
            new_v = [x for x in current if x != v]
            on_update_bridge(b['id'], {'vlans': new_v})

        return html.details({"open": False, "key": b["id"]},
                             html.summary({"className": "bridge-header"}, b["name"]),
                             html.div({"className": "bridge-details"},
                                      html.label({}, "Name"),
                                      html.input({
                                          "type": "text",
                                          "value": b["name"],
                                          "on_change": lambda e: on_update_bridge(b["id"], {"name": e['target']['value']})
                                      }),
                                      html.label({}, "Member Ports"),
                                      html.ul({}, *[html.li({}, port) for port in b.get("ports", [])]),
                                      html.label({}, "VLANs"),
                                      html.div({"className": "bridge-vlan-list"}, *[
                                          html.div({}, str(v), html.button({
                                              "className": "small",
                                              "style": {"marginLeft": "8px"},
                                              "onClick": (lambda e, vv=v: remove_vlan(vv))
                                          }, "Remove")) for v in (b.get("vlans", []) or [])
                                      ]),
                                      html.input({
                                          "type": "number",
                                          "placeholder": "Add VLAN ID",
                                          "min": 1,
                                          "max": 4094,
                                          "value": vlan_input,
                                          "on_change": lambda e: set_vlan_input(e['target']['value'])
                                      }),
                                      html.button({
                                          "className": "prop-button small info",
                                          "onClick": add_vlan
                                      }, "Add VLAN"),
                                      html.button({
                                          "className": "prop-button danger small",
                                          "onClick": lambda e: on_remove_bridge(b["id"]) 
                                      }, "Remove Bridge")
                                      )
                             )

    return html.div({"className": "prop-group"},
                    html.label({}, "Bridges"),
                    html.ul({}, *[BridgeItem(b) for b in (bridges or [])]),
                    html.button({
                        "id": "add-bridge-btn",
                        "className": "prop-button",
                        "onClick": lambda e: on_add_bridge()
                    }, "Add Bridge")
                    )


# ---------------- Services Panel (VPNs / Tunnels) ----------------
@component
def ServicesPanel(title, services, service_type, on_add_service, on_update_service, on_remove_service):
    return html.div({"className": "prop-group"},
                    html.label({}, title),
                    html.ul({},
                            *[
                                html.details({"open": False, "key": s["id"]},
                                             html.summary({"className": "service-header"}, s['name'],



                                                 ),
                                        html.div({"className": "service-details"},
                                                 html.label({}, "Name"),
                                                 html.input({
                                                     "type": "text",
                                                     "value": s["name"],
                                                     "on_change": lambda e, sid=s["id"]: on_update_service(sid, {
                                                         "name": e['target']['value']})
                                                 }),
                                                 html.label({}, "Remote IP/Destination"),
                                                 html.input({
                                                     "type": "text",
                                                     "value": s.get("remote", ""),
                                                     "placeholder": "e.g., 203.0.113.1",
                                                     "on_change": lambda e, sid=s["id"]: on_update_service(sid, {
                                                         "remote": e['target']['value']})
                                                 }),
                                                 html.button({
                                                     "className": "prop-button danger small",
                                                     "onClick": lambda e, sid=s["id"]: on_remove_service(sid)
                                                 }, f"Remove {service_type.upper()}")
                                                 )

                                             )
                                for s in services

                            ]
                            ),
                    html.button({
                        "id": f"add-{service_type.lower()}-btn",
                        "className": "prop-button info",
                        "onClick": lambda e: on_add_service()
                    }, f"Add {service_type}")
                    )


@component
def Dashboard():
    # Stateful dashboard with server-driven drag/drop and linking (no client JS)
    devices, set_devices = use_state([])
    links, set_links = use_state([])
    selected, set_selected = use_state(None)
    dragging, set_dragging = use_state({"id": None, "offset_x": 0, "offset_y": 0})
    linking, set_linking = use_state({"active": False, "start": None, "show_modal": False, "end": None})
    export_text, set_export_text = use_state("")
    import_text, set_import_text = use_state("")
    link_counter, set_link_counter = use_state(0)
    # connection UI state (for properties panel 'Create Connection')
    conn_src_port, set_conn_src_port = use_state(None)
    conn_tgt_device, set_conn_tgt_device = use_state(None)
    conn_tgt_port, set_conn_tgt_port = use_state(None)
    conn_link_type, set_conn_link_type = use_state('Ethernet')
    show_export, set_show_export = use_state(False)
    # context menu state for editing links
    link_context, set_link_context = use_state({"show": False, "link_id": None, "x": 0, "y": 0, "comment": "", "color": ""})
    show_link_menu, set_show_link_menu = use_state(False)
    link_menu_pos, set_link_menu_pos = use_state({"x": 0, "y": 0})
    link_menu_target, set_link_menu_target = use_state(None)
    menu_comment, set_menu_comment = use_state("")
    menu_color, set_menu_color = use_state("#ffffff")

    # Ensure any pre-existing state is normalized once at mount (fixes port id collisions
    # coming from older exports or fixtures). This runs once when the component mounts.
    hooks.use_effect(lambda: normalize_state(devices, links), [])

    # Device catalogue loaded from DB (seed from DEVICE_CATALOGUE if empty)
    catalogue_state, set_catalogue_state = use_state(None)

    def seed_and_load_catalogue():
        try:
            # local import to avoid module-level Django dependency issues
            from network.planning.models import DeviceModel
            # seed
            if DeviceModel.objects.count() == 0:
                for cat, items in DEVICE_CATALOGUE.items():
                    for item in items:
                        dm = DeviceModel(category=cat, type=item.get('type', ''), model=item.get('model', ''), ports=item.get('ports', 0), display=item.get('display', ''))
                        dm.save()
            # load and group
            qs = DeviceModel.objects.all().order_by('category', 'display')
            grouped = {}
            for m in qs:
                grouped.setdefault(m.category or 'Other', []).append({
                    'type': m.type,
                    'model': m.model,
                    'ports': m.ports,
                    'display': m.display
                })
            set_catalogue_state(grouped)
        except Exception:
            # fallback to in-memory constant if DB unavailable
            set_catalogue_state(DEVICE_CATALOGUE)

    hooks.use_effect(lambda: seed_and_load_catalogue(), [])

    # Link / interface type definitions
    link_types = ['Ethernet', 'DAC', 'AOC', 'Fibre', 'Wireless', 'VPN', 'VLAN', 'IP-IP Tunnel', 'IP Sec Tunnel', 'Routed']

    # Default interface type per device type
    default_port_iftype = {
        'Router': 'ethernet',
        'Switch': 'ethernet',
        'Server': 'ethernet',
        'Firewall': 'ethernet',
        'AP': 'wireless',
        'ONT': 'fibre',
        'Fibre': 'fibre',
        'NVR': 'ethernet',
        'DVR': 'ethernet'
    }

    # Compatibility matrix for interface types -> allowed link types
    allowed_links = {
        ('ethernet', 'ethernet'): ['Ethernet', 'DAC', 'AOC', 'VLAN', 'Routed'],
        ('ethernet', 'fibre'): ['Fibre'],
        ('fibre', 'fibre'): ['Fibre'],
        ('wireless', 'wireless'): ['Wireless'],
        ('ethernet', 'wireless'): ['Wireless'],
        ('ethernet', 'wan'): ['VPN', 'IP-IP Tunnel', 'IP Sec Tunnel', 'Routed'],
    }

    def get_port_iftype(device_item, port):
        if not port:
            return 'ethernet'
        if 'iftype' in port and port['iftype']:
            return port['iftype']
        return default_port_iftype.get(device_item.get('type'), 'ethernet')

    def allowed_link_types_for_ports(src_dev, src_port_id, tgt_dev, tgt_port_id):
        s_port = next((p for p in src_dev['ports'] if p['id'] == src_port_id), None)
        t_port = next((p for p in tgt_dev['ports'] if p['id'] == tgt_port_id), None)
        s_if = get_port_iftype(src_dev, s_port)
        t_if = get_port_iftype(tgt_dev, t_port)
        pair = (s_if, t_if)
        pair_rev = (t_if, s_if)
        if pair in allowed_links:
            return allowed_links[pair]
        if pair_rev in allowed_links:
            return allowed_links[pair_rev]
        # fallback heuristics
        if 'fibre' in (s_if, t_if):
            return ['Fibre']
        return ['Ethernet', 'VLAN', 'Routed']

    def add_device(item):
        # normalize ports and attach interface types; ensure port IDs include device id
        ports_list = []
        ports = item.get("ports", [])
        dev_iftype = item.get('port_iftype') or default_port_iftype.get(item.get('type'), 'ethernet')
        device_id = f"dev{len(devices) + 1}"
        if isinstance(ports, int):
            ports_list = [
                {"id": f"port-{device_id}-{i}", "name": f"ether{i}", "ips": [], "vlans": [], "bridge": None, 'iftype': dev_iftype}
                for i in range(1, ports + 1)
            ]
        elif isinstance(ports, list):
            ports_list = []
            for i, p in enumerate(ports, start=1):
                if isinstance(p, dict):
                    entry = dict(p)
                    if 'id' not in entry:
                        entry['id'] = f"port-{device_id}-{i}"
                    if 'iftype' not in entry:
                        entry['iftype'] = dev_iftype
                else:
                    entry = {"id": f"port-{device_id}-{i}", "name": str(p), "ips": [], "vlans": [], "bridge": None, 'iftype': dev_iftype}
                ports_list.append(entry)

        new_device = {
            "id": device_id,
            "name": item.get("name", "Device"),
            "type": item.get("type", "generic"),
            "x": 50,
            "y": 50,
            "ports": ports_list,
            "bridges": [],
            "vpns": [],
            "ipTunnels": [],
        }
        set_devices(devices + [new_device])

    def update_device_property(dev_id, updates):
        updated = []
        for d in devices:
            if d['id'] == dev_id:
                dn = dict(d)
                dn.update(updates)
                updated.append(dn)
            else:
                updated.append(d)
        set_devices(updated)

    def update_port(dev_id, port_id, updates):
        # update a single port object on a device (persist to central state)
        updated_devices = []
        for d in devices:
            if d['id'] == dev_id:
                nd = dict(d)
                nd_ports = []
                for p in d.get('ports', []):
                    if p.get('id') == port_id:
                        np = dict(p)
                        np.update(updates)
                        nd_ports.append(np)
                        # If the port's bridge assignment changed, update bridge membership lists
                        if 'bridge' in updates:
                            new_bridge = updates.get('bridge')
                            # remove this port from any other bridges on this device
                            for br in nd.get('bridges', []):
                                if port_id in br.get('ports', []):
                                    if br.get('id') != new_bridge:
                                        br['ports'] = [x for x in br.get('ports', []) if x != port_id]
                            # add to the target bridge if set
                            if new_bridge:
                                tb = next((b for b in nd.get('bridges', []) if b['id'] == new_bridge), None)
                                if tb and port_id not in tb.get('ports', []):
                                    tb.setdefault('ports', []).append(port_id)
                    else:
                        nd_ports.append(p)
                nd['ports'] = nd_ports
                updated_devices.append(nd)
            else:
                updated_devices.append(d)
        set_devices(updated_devices)

    def update_bridge(dev_id, bridge_id, updates):
        # update a single bridge object on a device (e.g., vlans, name)
        updated_devices = []
        for d in devices:
            if d['id'] == dev_id:
                nd = dict(d)
                nd_bridges = []
                for b in nd.get('bridges', []):
                    if b.get('id') == bridge_id:
                        nb = dict(b)
                        nb.update(updates)
                        nd_bridges.append(nb)
                    else:
                        nd_bridges.append(b)
                nd['bridges'] = nd_bridges
                updated_devices.append(nd)
            else:
                updated_devices.append(d)
        set_devices(updated_devices)

    def remove_device_property(dev_id, prop_type, item_id):
        updated = []
        for d in devices:
            if d['id'] == dev_id:
                dn = dict(d)
                # when removing a bridge, also clear bridge assignment on ports
                if prop_type == 'bridges':
                    dn[prop_type] = [x for x in dn[prop_type] if x['id'] != item_id]
                    for p in dn.get('ports', []):
                        if p.get('bridge') == item_id:
                            p['bridge'] = None
                else:
                    dn[prop_type] = [x for x in dn[prop_type] if x['id'] != item_id]
                updated.append(dn)
            else:
                updated.append(d)
        set_devices(updated)

    def add_bridge_to_device(dev_id):
        updated = []
        for d in devices:
            if d['id'] == dev_id:
                dn = dict(d)
                new_bridge = {"id": f"bridge-{len(dn['bridges'])}", "name": f"Bridge {len(dn['bridges']) + 1}",
                              "ports": [], "vlans": []}
                dn['bridges'].append(new_bridge)
                updated.append(dn)
            else:
                updated.append(d)
        set_devices(updated)

    def add_service_to_device(device_id, service_type):
        dn = next((d for d in devices if d["id"] == device_id), None)
        if not dn:
            return

        # Map service type → correct key
        type_map = {
            "VPN": "vpns",
            "Tunnel": "ipTunnels",
        }
        key = type_map[service_type]

        if key not in dn:
            dn[key] = []

        services = dn[key]
        new_service = {
            "id": f"{service_type.lower()}-{len(services)}",
            "name": f"{service_type} {len(services) + 1}",
            "remote": "",
            "type": service_type
        }
        services.append(new_service)
        set_devices(devices[:])  # re-render

    def on_toggle_link():
        s = dict(linking)
        s['active'] = not s['active']
        s['start'] = None
        s['end'] = None
        s['show_modal'] = False
        set_linking(s)

    def on_device_mouse_down(dev_id, e):
        # start dragging this device; compute offset from mouse
        client_x = e.get('clientX', 0)
        client_y = e.get('clientY', 0)
        dev = next((d for d in devices if d['id'] == dev_id), None)
        if not dev:
            return
        set_dragging({'id': dev_id, 'offset_x': client_x - dev['x'], 'offset_y': client_y - dev['y']})

    def on_canvas_mouse_move(e):
        if not dragging['id']:
            return
        client_x = e.get('clientX', 0)
        client_y = e.get('clientY', 0)
        new_x = client_x - dragging['offset_x']
        new_y = client_y - dragging['offset_y']
        updated = []
        for d in devices:
            if d['id'] == dragging['id']:
                dn = dict(d)
                dn['x'] = max(0, new_x)
                dn['y'] = max(0, new_y)
                updated.append(dn)
            else:
                updated.append(d)
        set_devices(updated)

    def on_canvas_mouse_up(e):
        if dragging['id']:
            set_dragging({'id': None, 'offset_x': 0, 'offset_y': 0})

    def select_device(dev_id):
        set_selected(dev_id)

    def delete_device(dev_id):
        set_devices([d for d in devices if d['id'] != dev_id])
        set_links([l for l in links if l['sourceDeviceId'] != dev_id and l['targetDeviceId'] != dev_id])
        if selected == dev_id:
            set_selected(None)

    def port_clicked(dev_id, port_id):
        s = dict(linking)
        if not s['active']:
            return
        if s['start'] is None:
            s['start'] = {'deviceId': dev_id, 'portId': port_id}
            set_linking(s)
        else:
            # set end and open modal to choose link type
            s['end'] = {'deviceId': dev_id, 'portId': port_id}
            s['show_modal'] = True
            set_linking(s)

    def remove_port_from_device(dev_id, port_id):
        updated = []
        for d in devices:
            if d['id'] == dev_id:
                dn = dict(d)
                # remove the port
                dn['ports'] = [p for p in dn.get('ports', []) if p.get('id') != port_id]
                # remove port from any bridge membership
                for br in dn.get('bridges', []):
                    if port_id in br.get('ports', []):
                        br['ports'] = [x for x in br.get('ports', []) if x != port_id]
                updated.append(dn)
            else:
                updated.append(d)
        set_devices(updated)

    def add_port_to_device(dev_id):
        updated = []
        for d in devices:
            if d['id'] == dev_id:
                ports = list(d['ports'])
                # determine default interface type for this device
                dev_iftype = default_port_iftype.get(d.get('type'), '')
                pid = f"port-{dev_id}-{len(ports) + 1}"
                ports.append({
                    "id": pid,
                    "name": f"ether{len(ports) + 1}",
                    "ips": [],
                    "vlans": [],
                    "bridge": None,
                    "iftype": dev_iftype
                })
                updated.append({**d, "ports": ports})
            else:
                updated.append(d)
        set_devices(updated)

    def confirm_create_link(link_type):
        s = dict(linking)
        if not s.get('start') or not s.get('end'):
            return
        # validate compatibility between selected ports
        src_dev = next((d for d in devices if d['id'] == s['start']['deviceId']), None)
        tgt_dev = next((d for d in devices if d['id'] == s['end']['deviceId']), None)
        allowed = allowed_link_types_for_ports(src_dev, s['start']['portId'], tgt_dev, s['end']['portId']) if src_dev and tgt_dev else []
        if link_type not in allowed:
            # incompatible -> cancel and do not create
            set_linking({'active': False, 'start': None, 'end': None, 'show_modal': False})
            return
        # create link
        lid = f"link-{link_counter}"
        new_link = {
            'id': lid,
            'sourceDeviceId': s['start']['deviceId'],
            'sourcePortId': s['start']['portId'],
            'targetDeviceId': s['end']['deviceId'],
            'targetPortId': s['end']['portId'],
            'linkType': link_type,
            'color': '#99cc00',
            'ips': []
        }
        set_links(links + [new_link])
        set_link_counter(link_counter + 1)
        set_linking({'active': False, 'start': None, 'end': None, 'show_modal': False})

    # Programmatic helper: create a connection between two ports (used by properties UI)
    def create_connection(src_dev_id, src_port_id, tgt_dev_id, tgt_port_id, link_type):
        src_dev = next((d for d in devices if d['id'] == src_dev_id), None)
        tgt_dev = next((d for d in devices if d['id'] == tgt_dev_id), None)
        if not src_dev or not tgt_dev:
            return False
        allowed = allowed_link_types_for_ports(src_dev, src_port_id, tgt_dev, tgt_port_id)
        if link_type not in allowed:
            return False
        lid = f"link-{link_counter}"
        new_link = {
            'id': lid,
            'sourceDeviceId': src_dev_id,
            'sourcePortId': src_port_id,
            'targetDeviceId': tgt_dev_id,
            'targetPortId': tgt_port_id,
            'linkType': link_type,
            'color': '#99cc00',
            'ips': []
        }
        set_links(links + [new_link])
        set_link_counter(link_counter + 1)
        return True

    def cancel_link_modal():
        set_linking({'active': False, 'start': None, 'end': None, 'show_modal': False})

    def prepare_export():
        import json
        state = {'devices': devices, 'links': links}
        set_export_text(json.dumps(state, indent=2))

    def load_import_text():
        import json
        try:
            state = json.loads(import_text)
            if 'devices' in state and 'links' in state:
                set_devices(state['devices'])
                set_links(state['links'])
                # normalize any imported state to ensure ports ids are unique per-device
                try:
                    normalize_state(state['devices'], state['links'])
                except Exception:
                    pass
        except Exception:
            # ignore invalid JSON for now
            pass

    def normalize_state(devs, lks):
        # Ensure each port id is unique and scoped to its device; update links accordingly.
        # Use a per-device mapping so identical old port ids on different devices don't
        # collide when remapping (older exports sometimes used simple names like "ether1").
        id_map = {}
        new_devices = []
        for d_idx, d in enumerate(devs):
            device_id = d.get('id') or f"dev{d_idx+1}"
            ports = []
            id_map.setdefault(device_id, {})
            for idx, p in enumerate(d.get('ports', []), start=1):
                old_id = p.get('id')
                # if the port id doesn't include the device id, remap it to a device-scoped id
                if not old_id or str(device_id) not in str(old_id):
                    new_id = f"port-{device_id}-{idx}"
                else:
                    new_id = old_id
                # store mapping under the device to avoid cross-device collisions
                id_map[device_id][old_id] = new_id
                np = dict(p)
                np['id'] = new_id
                ports.append(np)
            nd = dict(d)
            nd['id'] = device_id
            nd['ports'] = ports
            new_devices.append(nd)

        # update links to point to new port ids using the link's device context
        new_links = []
        for lk in lks:
            nl = dict(lk)
            s_old = nl.get('sourcePortId')
            t_old = nl.get('targetPortId')
            s_dev = nl.get('sourceDeviceId')
            t_dev = nl.get('targetDeviceId')
            if s_dev and s_dev in id_map and s_old in id_map[s_dev]:
                nl['sourcePortId'] = id_map[s_dev][s_old]
            if t_dev and t_dev in id_map and t_old in id_map[t_dev]:
                nl['targetPortId'] = id_map[t_dev][t_old]
            new_links.append(nl)

        # if anything changed, write back
        if new_devices != devs:
            set_devices(new_devices)
        if new_links != lks:
            set_links(new_links)

    def open_link_context(link_id, e=None):
        # prevent browser context menu (event may not be a real browser event here)
        try:
            if e and 'preventDefault' in e:
                e['preventDefault']()
        except Exception:
            pass
        set_link_context({'linkId': link_id})

    def save_link_context(link_id, comment, color):
        updated = []
        for l in links:
            if l['id'] == link_id:
                nl = dict(l)
                nl['comment'] = comment
                nl['color'] = color
                updated.append(nl)
            else:
                updated.append(l)
        set_links(updated)
        set_link_context(None)

    # build UI
    header = html.div({"className": "header"},
                      html.img({"src": "https://placehold.co/100x40/000000/99cc00?text=Logo", "alt": "Logo"}),
                      "Next Level Networks - Network Planning Tool",
                      html.button({"className": "toolbar-button", "style": {"marginLeft": "10px"},
                                   "onClick": lambda e: set_show_export(not show_export)}, "Toggle Export/Import"))

    # toolbar/sidebar
    sidebar = Sidebar(on_add_device=add_device, on_toggle_link=on_toggle_link, linking_active=linking['active'], catalogue=catalogue_state)

    # canvas
    svg_children = []
    # compute simple straight-line links
    # link visuals: transit description + stroke color and strokeWidth
    link_visuals = {
        'Ethernet': {'transit': 'L2 (Ethernet)', 'stroke': '#ffffff', 'strokeWidth': 3},
        'DAC': {'transit': 'L1 (DAC)', 'stroke': '#b0b0b0', 'strokeWidth': 3},
        'AOC': {'transit': 'L1 (AOC)', 'stroke': '#9fe6ff', 'strokeWidth': 3},
        'Fibre': {'transit': 'L1 (Fibre)', 'stroke': '#66ccff', 'strokeWidth': 3},
        'Wireless': {'transit': 'Wireless', 'stroke': '#ffaa00', 'strokeWidth': 3},
        'VPN': {'transit': 'IP (VPN)', 'stroke': '#0077cc', 'strokeWidth': 3},
        'VLAN': {'transit': 'L2 (VLAN)', 'stroke': '#ff8800', 'strokeWidth': 3},
        'IP-IP Tunnel': {'transit': 'IP Tunnel', 'stroke': '#aa00ff', 'strokeWidth': 3},
        'IP Sec Tunnel': {'transit': 'IP Sec Tunnel', 'stroke': '#8800aa', 'strokeWidth': 3},
        'Routed': {'transit': 'IP (Routed)', 'stroke': '#99cc00', 'strokeWidth': 3},
        'Tunnel': {'transit': 'Tunnel', 'stroke': '#aa00ff', 'strokeWidth': 3}
    }

    # port size (increased by 3px as requested)
    port_w = 16 + 3
    port_h = 15 + 3
    padding = 4

    def device_layout(device):
        # fixed number of columns, rows computed from ports
        cols = 4
        num = len(device.get('ports', []))
        import math
        rows = max(1, math.ceil(num / cols))
        dev_w = max(70, int(cols * port_w + (cols + 1) * padding))
        dev_h = max(70, int(rows * port_h + (rows + 1) * padding))
        cell_w = dev_w / cols
        cell_h = dev_h / rows
        return cols, rows, dev_w, dev_h, cell_w, cell_h

    def port_pos(device, idx):
        cols, rows, dev_w, dev_h, cell_w, cell_h = device_layout(device)
        col = idx % cols
        row = idx // cols
        x = device['x'] + col * cell_w + (cell_w - port_w) / 2 + port_w / 2
        y = device['y'] + row * cell_h + (cell_h - port_h) / 2 + port_h / 2
        return x, y

    for l in links:
        src = next((d for d in devices if d['id'] == l['sourceDeviceId']), None)
        tgt = next((d for d in devices if d['id'] == l['targetDeviceId']), None)
        if not src or not tgt:
            continue
        # find port indices
        try:
            s_idx = next(i for i, p in enumerate(src['ports']) if p['id'] == l['sourcePortId'])
            t_idx = next(i for i, p in enumerate(tgt['ports']) if p['id'] == l['targetPortId'])
        except StopIteration:
            continue

        x1, y1 = port_pos(src, s_idx)
        x2, y2 = port_pos(tgt, t_idx)
        path = f"M {x1} {y1} L {x2} {y2}"
        # Determine a human-friendly transit layer and stroke for the tooltip and visual
        v = link_visuals.get(l.get('linkType'), {})
        transit = v.get('transit', l.get('linkType') or 'Unknown')
        # prefer explicit link color when present, otherwise fall back to visuals
        stroke = l.get('color') or v.get('stroke') or '#ffffff'
        stroke_w = v.get('strokeWidth', 3)
        left_label = f"{src.get('name') or src.get('id')}:{l.get('sourcePortId')}"
        right_label = f"{tgt.get('name') or tgt.get('id')}:{l.get('targetPortId')}"
        # include IPs and comment if available
        ips = l.get('ips') or []
        ips_text = ', '.join(ips) if ips else ''
        comment = l.get('comment') or ''
        title_lines = [f"{left_label} ↔ {right_label}", f"Transit: {transit}"]
        if ips_text:
            title_lines.append(f"IPs: {ips_text}")
        if comment:
            title_lines.append(f"Note: {comment}")
        title_text = '\n'.join(title_lines)
        # group path + title so the title shows on hover
        # attach right-click handler to path to open link editor
        # use onContextMenu (ReactPy lower-case event) and prevent default to show custom menu
        def _make_oncontext(lid):
            @event(prevent_default=True, stop_propagation=True)
            def _handler(e):
                # suppress default browser menu
                try:
                    if hasattr(e, "prevent_default"):
                        e.prevent_default()
                    elif isinstance(e, dict) and "preventDefault" in e:
                        e["preventDefault"]()
                except Exception:
                    pass

                # capture position and show custom menu
                x = e.get("clientX", 0) if hasattr(e, "get") else getattr(e, "clientX", 0)
                y = e.get("clientY", 0) if hasattr(e, "get") else getattr(e, "clientY", 0)
                set_link_menu_pos({"x": int(x or 0), "y": int(y or 0)})
                set_link_menu_target(lid)
                set_show_link_menu(True)

            return _handler

        @event(prevent_default=True, stop_propagation=True)
        def _cancel_contextmenu(e):
            # Always block the browser's right-click menu
            try:
                e.prevent_default()
            except Exception:
                pass

        def _make_onmousedown(lid):
            @event(prevent_default=True, stop_propagation=True)
            def _handler(e):
                # Some environments deliver mouse button info on mouse down instead of contextmenu
                try:
                    btn = None
                    if hasattr(e, 'get'):
                        btn = e.get('button', None)
                    else:
                        btn = getattr(e, 'button', None)
                    # right-click is button 2 (or sometimes 3); accept 2
                    if btn == 2:
                        _open_menu_from_event(lid, e)
                except Exception:
                    # fallback: open menu anyway
                    _open_menu_from_event(lid, e)

            return _handler

        def _open_menu_from_event(lid, e):
            # unified logic to prevent default and set menu position/state
            try:
                if hasattr(e, 'prevent_default'):
                    e.prevent_default()
            except Exception:
                pass
            try:
                if 'preventDefault' in e:
                    e['preventDefault']()
            except Exception:
                pass
            x = 0
            y = 0
            try:
                if hasattr(e, 'get'):
                    x = e.get('clientX', 0)
                    y = e.get('clientY', 0)
                else:
                    x = getattr(e, 'clientX', 0)
                    y = getattr(e, 'clientY', 0)
            except Exception:
                pass
            set_link_menu_pos({'x': int(x or 0), 'y': int(y or 0)})
            set_link_menu_target(lid)
            # initialize inline editor fields from the link if available
            try:
                if lid and lid != 'demo':
                    link_item = next((li for li in links if li.get('id') == lid), None)
                    if link_item:
                        set_menu_comment(link_item.get('comment', ''))
                        set_menu_color(link_item.get('color', link_visuals.get(link_item.get('linkType'), {}).get('stroke', '#ffffff')))
                    else:
                        set_menu_comment("")
                        set_menu_color('#ffffff')
                else:
                    set_menu_comment("")
                    set_menu_color('#ffffff')
            except Exception:
                set_menu_comment("")
                set_menu_color('#ffffff')
            set_show_link_menu(True)


        # draw a visible path and a wider invisible hit-path on top to improve pointer accuracy
        visible_path = svg.path({
            "d": path,
            "stroke": stroke,
            "strokeWidth": str(stroke_w),
            "fill": "none",
            # keep visible path non-interactive so events are handled by the hit path
            "style": {"pointerEvents": "none"},
            "zIndex": 1000,
        })

        hit_path = svg.path({
            "d": path,
            "stroke": stroke,
            "strokeWidth": str(stroke_w + 3),
            "strokeOpacity": "0",
            "fill": "none",
            "style": {"cursor": "pointer", "pointerEvents": "stroke"},
            "onContextMenu": _make_oncontext(l['id'])

        })

        svg_children.append(svg.g({}, svg.title({}, title_text), visible_path, hit_path))

    # add device SVG groups into svg_children so devices render inside the SVG canvas
    for d in devices:
        dev_x = d.get('x', 0)
        dev_y = d.get('y', 0)
        cols, rows, dev_w, dev_h, cell_w, cell_h = device_layout(d)

        # device body sized according to number of ports
        device_body = svg.rect({"x": 0, "y": 0, "width": dev_w, "height": dev_h, "rx": 8, "ry": 8,
                                 "fill": "#2b2b2b", "stroke": "#676767", "strokeWidth": "2"})

        # ports as rects inside device (larger by 3px)
        port_elements = []
        for i, p in enumerate(d['ports']):
            port_id = p['id']
            col = i % cols
            row = i // cols
            px = col * cell_w + (cell_w - port_w) / 2
            py = row * cell_h + (cell_h - port_h) / 2
            # determine if this port is connected
            connected = any(
                (l.get('sourceDeviceId') == d['id'] and l.get('sourcePortId') == port_id) or
                (l.get('targetDeviceId') == d['id'] and l.get('targetPortId') == port_id)
                for l in links
            )
            fill_color = '#008000' if connected else '#aa0000'
            iface_name = p.get('name') or port_id
            ip_addr = ''
            if p.get('ips'):
                try:
                    ip_addr = p.get('ips')[0] if len(p.get('ips')) else ''
                except Exception:
                    ip_addr = ''
            title_text = f"{iface_name}" + (f" — {ip_addr}" if ip_addr else "")
            port_rect = svg.rect({"x": 0, "y": 0, "width": port_w, "height": port_h, "fill": fill_color,
                                  "rx": 3, "ry": 3, "stroke": "#333", "strokeWidth": "1",
                                  "onClick": (lambda e, did=d['id'], pid=port_id: port_clicked(did, pid))})
            port_el = svg.g({"transform": f"translate({px},{py})"}, svg.title({}, title_text), port_rect)
            port_elements.append(port_el)

        # device label centered
        label = svg.text({"x": dev_w / 2, "y": dev_h - 6, "fontSize": 10, "fill": "#fff", "textAnchor": "middle"}, d.get('name') or d.get('id'))

        # attach mouse handlers to the group so device is clickable/draggable even when ports overlay it
        dev_group = svg.g({"transform": f"translate({dev_x},{dev_y})", "id": d['id'],
                           "on_mouse_down": (lambda e, did=d['id']: on_device_mouse_down(did, e)),
                           "onClick": (lambda e, did=d['id']: select_device(did)),
                           "style": {"cursor": "grab"}}, device_body, *port_elements, label)
        svg_children.append(dev_group)


    svg_root = svg.svg({"width": "100%", "height": "100%", "style": {"position": "absolute", "top": "0", "left": "0"}}, *svg_children)

    # canvas: capture clicks to hide context menu and attach mouse handlers
    @event(prevent_default=True, stop_propagation=True)
    def handle_canvas_click(e):
        if show_link_menu:
            set_show_link_menu(False)

    @event(prevent_default=True, stop_propagation=True)
    def canvas_oncontext(e):
        # prevent browser context menu anywhere in the canvas; element handlers may still open custom menu
        return None

    # Render inline context editor for links (positioned absolute inside canvas)
    if show_link_menu and link_menu_target:
        def save_menu(e):
            lid = link_menu_target
            # update the link with new comment/color
            updated = []
            for l in links:
                if l['id'] == lid:
                    nl = dict(l)
                    nl['comment'] = menu_comment
                    nl['color'] = menu_color
                    updated.append(nl)
                else:
                    updated.append(l)
            set_links(updated)
            set_show_link_menu(False)

        def delete_menu(e):
            lid = link_menu_target
            set_links([l for l in links if l['id'] != lid])
            set_show_link_menu(False)

        def cancel_menu(e):
            set_show_link_menu(False)

        editor_panel = html.div({"style": {"position": "absolute", "top": f"{link_menu_pos['y']}px", "left": f"{link_menu_pos['x']}px", "padding": "10px", "background": "#fff", "border": "1px solid #ccc", "borderRadius": "8px", "zIndex": "1000"}},
                                 html.h4({}, f"Edit Link"),
                                 html.label({}, "Comment:"),
                                 html.input({"type": "text", "value": menu_comment, "on_change": lambda e: set_menu_comment(e['target']['value'])}),
                                 html.br(),
                                 html.label({}, "Color:"),
                                 html.input({"type": "color", "value": menu_color, "on_change": lambda e: set_menu_color(e['target']['value'])}),
                                 html.br(),
                                 html.button({"type": "button", "onClick": save_menu}, "Save"),
                                 html.button({"type": "button", "onClick": delete_menu, "style": {"marginLeft": "8px", "background": "#f66"}}, "Delete"),
                                 html.button({"type": "button", "onClick": cancel_menu, "style": {"marginLeft": "8px"}}, "Cancel")
                                 )
        canvas = html.div({"id": "canvas", "style": {"position": "relative", "flexGrow": 1, "backgroundColor": "#000",
                             "backgroundImage": "linear-gradient(#676767 1px, transparent 1px), linear-gradient(90deg, #676767 1px, transparent 1px)",
                             "backgroundSize": "25px 25px", "overflow": "hidden"},
                       "on_mouse_move": on_canvas_mouse_move, "on_mouse_up": on_canvas_mouse_up,  "onContextMenu": canvas_oncontext}, svg_root, editor_panel)
    else:
        canvas = html.div({"id": "canvas", "style": {"position": "relative", "flexGrow": 1, "backgroundColor": "#000",
                             "backgroundImage": "linear-gradient(#676767 1px, transparent 1px), linear-gradient(90deg, #676767 1px, transparent 1px)",
                             "backgroundSize": "25px 25px", "overflow": "hidden"},
                       "on_mouse_move": on_canvas_mouse_move, "on_mouse_up": on_canvas_mouse_up, "onContextMenu": canvas_oncontext}, svg_root)

    # properties panel
    props = []
    sel = next((d for d in devices if d['id'] == selected), None)

    if sel:
        # Basic info
        for p in sel['ports']:
            props.append(
                PortItem(
                    port=p,
                    device_id=sel['id'],
                    key=p['id'],
                    on_update_port=lambda port_id, updated: update_port(sel['id'], port_id, updated),
                    on_update_bridge=lambda bid, bridge_updates: update_bridge(sel['id'], bid, bridge_updates),
                    on_remove_port=lambda port_id: remove_port_from_device(sel['id'], port_id),
                    bridges=sel.get('bridges', []),
                    on_add_port=add_port_to_device
                )
            )
        props.append(html.div({"className": "prop-group"},
                              html.label({}, "Device Name"),
                              html.input({"type": "text", "value": sel['name'],
                                          "on_change": lambda e: update_device_property(sel['id'], {
                                              'name': e['target']['value']})})))
        # Coordinates
        props.append(html.div({"className": "prop-group"},
                              html.label({}, "X"),
                              html.input({"type": "number", "value": sel['x'],
                                          "on_change": lambda e: update_device_property(sel['id'], {
                                              'x': int(e['target']['value'] or 0)})}),
                              html.label({}, "Y"),
                              html.input({"type": "number", "value": sel['y'],
                                          "on_change": lambda e: update_device_property(sel['id'], {
                                              'y': int(e['target']['value'] or 0)})})))

        # Bridges
        props.append(BridgesPanel(
            bridges=sel.get('bridges', []),
            on_add_bridge=lambda: add_bridge_to_device(sel['id']),
            on_update_bridge=lambda bid, upd: update_device_property(sel['id'], {'bridges': [
                {**b, **upd} if b['id'] == bid else b for b in sel['bridges']
            ]}),
            on_remove_bridge=lambda bid: remove_device_property(sel['id'], 'bridges', bid)
        ))

        # VPNs
        props.append(ServicesPanel(
            title="VPNs",
            services=sel.get('vpns', []),
            service_type="VPN",
            on_add_service=lambda: add_service_to_device(sel['id'], "VPN"),
            on_update_service=lambda sid, upd: update_device_property(sel['id'], {'vpns': [
                {**s, **upd} if s['id'] == sid else s for s in sel['vpns']
            ]}),
            on_remove_service=lambda sid: remove_device_property(sel['id'], 'vpns', sid)
        ))

        # IP Tunnels
        props.append(ServicesPanel(
            title="IP Tunnels",
            services=sel.get('ipTunnels', []),
            service_type="Tunnel",
            on_add_service=lambda: add_service_to_device(sel['id'], "Tunnel"),
            on_update_service=lambda sid, upd: update_device_property(sel['id'], {'ipTunnels': [
                {**s, **upd} if s['id'] == sid else s for s in sel['ipTunnels']
            ]}),
            on_remove_service=lambda sid: remove_device_property(sel['id'], 'ipTunnels', sid)
        ))

        # Create Connection (properties panel helper)
        # Source port selector (from selected device)
        props.append(html.div({"className": "prop-group"}, html.label({}, "Create Connection (manual)")))
        # Source port selector with placeholder
        props.append(html.div({"className": "prop-group"}, html.label({}, "Source Port"), html.select({"value": conn_src_port or "", "on_change": lambda e: set_conn_src_port(e['target']['value'])}, html.option({"value": ""}, "(select a source port)"), *[html.option({"value": p['id']}, p.get('name') or p['id']) for p in sel['ports']])))
        # Target device selector (exclude selected device) with placeholder / no-devices message
        other_devs = [d for d in devices if d['id'] != sel['id']]
        target_options = [html.option({"value": ""}, "(select a target device)")]
        if other_devs:
            target_options += [html.option({"value": d['id']}, d.get('name') or d['id']) for d in other_devs]
        else:
            target_options = [html.option({"value": "", "disabled": True}, "(no other devices available)")]
        props.append(html.div({"className": "prop-group"}, html.label({}, "Target Device"), html.select({"value": conn_tgt_device or "", "on_change": lambda e: (set_conn_tgt_device(e['target']['value']), set_conn_tgt_port(None))}, *target_options)))
        # Target port selector (populated from chosen device)
        tgt_ports = []
        if conn_tgt_device:
            tgt_dev = next((d for d in devices if d['id'] == conn_tgt_device), None)
            if tgt_dev:
                tgt_ports = tgt_dev['ports']
        props.append(html.div({"className": "prop-group"}, html.label({}, "Target Port"), html.select({"value": conn_tgt_port or "", "on_change": lambda e: set_conn_tgt_port(e['target']['value'])}, *([html.option({"value": p['id']}, p['name']) for p in tgt_ports] if tgt_ports else [html.option({"value": ""}, "(select a device first)")]))))
        # Link type selector filtered by compatibility
        allowed_for_selection = []
        if conn_src_port and conn_tgt_device and conn_tgt_port:
            src_dev = sel
            tgt_dev = next((d for d in devices if d['id'] == conn_tgt_device), None)
            if tgt_dev:
                allowed_for_selection = allowed_link_types_for_ports(src_dev, conn_src_port, tgt_dev, conn_tgt_port)
        # fallback to all link types
        if not allowed_for_selection:
            allowed_for_selection = link_types
        props.append(html.div({"className": "prop-group"}, html.label({}, "Link Type"), html.select({"value": conn_link_type, "on_change": lambda e: set_conn_link_type(e['target']['value'])}, *[html.option({"value": lt}, lt) for lt in allowed_for_selection])))
        # Create button
        can_create = bool(conn_src_port and conn_tgt_device and conn_tgt_port)
        props.append(html.div({"className": "prop-group"}, html.button({"className": "prop-button", "onClick": lambda e: create_connection(sel['id'], conn_src_port, conn_tgt_device, conn_tgt_port, conn_link_type) if can_create else None, "disabled": not can_create}, "Create Connection")))

    properties_panel = html.div({"id": "properties-panel",
                                 "style": {"width": "300px", "backgroundColor": "#111", "padding": "15px",
                                           "borderLeft": "2px solid #676767", "overflowY": "auto"}}, *props)

    # link modal
    link_modal = None
    if linking['show_modal'] and linking.get('start') and linking.get('end'):
        s = linking['start']
        e = linking['end']
        link_modal = html.div({"className": "modal-backdrop"},
                              html.div({"className": "modal-content"}, html.h3({}, "Create Link"),
                                       html.div({}, html.p({}, f"From: {s['deviceId']} {s['portId']}"),
                                                html.p({}, f"To: {e['deviceId']} {e['portId']}")), html.div({}, *[
                                      html.button({"className": "prop-button",
                                                   "onClick": (lambda lt=lt: confirm_create_link(lt))}, lt) for lt in
                                      ["Ethernet", "Fibre", "VPN", "VLAN", "Routed"]]),
                                       html.div({"style": {"marginTop": "8px"}}, html.button(
                                           {"className": "prop-button danger",
                                            "onClick": lambda ev: cancel_link_modal()}, "Cancel"))))

    # export/import UI
    export_ui = html.div({"style": {"padding": "10px"}}, html.h3({}, "Export / Import JSON"),
                         html.button({"onClick": lambda e: prepare_export()}, "Prepare Export"), html.div({},
                                                                                                           html.textarea(
                                                                                                               {
                                                                                                                   "rows": 10,
                                                                                                                   "style": {
                                                                                                                       "width": "100%"},
                                                                                                                   "value": export_text,
                                                                                                                   "readOnly": True})),
                         html.label({}, "Paste JSON to import:"), html.textarea(
            {"rows": 8, "style": {"width": "100%"}, "value": import_text,
             "on_change": lambda e: set_import_text(e['target']['value'])}),
                         html.button({"onClick": lambda e: load_import_text()}, "Load from text"))

    footer_children = []
    if show_export:
        footer_children.append(export_ui)

    # link context modal (right-click on a link to edit)
    link_context_modal = None
    if link_context and link_context.get('linkId'):
        lid = link_context['linkId']
        link_item = next((li for li in links if li['id'] == lid), None)
        if link_item:
            # local state values for modal are stored in the link object; use inputs to change
            current_comment = link_item.get('comment', '')
            current_color = link_item.get('color', link_visuals.get(link_item.get('linkType'), {}).get('stroke', '#ffffff'))
            # render modal
            link_context_modal = html.div({"className": "modal-backdrop"},
                                          html.div({"className": "modal-content"}, html.h3({}, "Edit Link"),
                                                   html.div({"className": "prop-group"}, html.label({}, "Comment"), html.input({"type": "text", "value": current_comment, "on_change": lambda e, lid=lid: save_link_context(lid, e['target']['value'], current_color)})),
                                                   html.div({"className": "prop-group"}, html.label({}, "Color"), html.input({"type": "color", "value": current_color, "on_change": lambda e, lid=lid: save_link_context(lid, current_comment, e['target']['value'])})),
                                                   html.div({"style": {"marginTop": "8px"}}, html.button({"className": "prop-button", "onClick": lambda e, lid=lid: set_link_context(None)}, "Cancel"))))

    return ThemeSwitcher(
        html.div({"className": "dashboard", "style": {"display": "flex", "flexDirection": "column", "height": "100vh"}},
                 header,
                 html.div({"className": "main-container", "style": {"display": "flex", "flex": 1}}, sidebar, canvas,
                          properties_panel), link_modal, *footer_children))


# todo hover on port show ip
# todo hover on link show ip & add comment
# todo change color of links add a legend
# todo toggle display of import and export panel
