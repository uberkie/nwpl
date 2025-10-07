from reactpy import component, html, hooks, use_state


def Sidebar(on_add_device=None, on_toggle_link=None, linking_active=False):
    # Sidebar now accepts callbacks from Dashboard so actions are server-driven
    return html.div(
        {"className": "sidebar", "style": {"overflowY": "auto", "maxHeight": "100vh"}},  # Added scroll

        html.div({"className": "toolbar"},
                 html.h3({}, "Device Catalogue"),
                 html.div({"className": "device-catalogue"}, DeviceCatalogue(on_add_device)),
                 html.hr(),
                 html.h3({}, "Device Filters"),
                 html.div({"id": "device-filter-group", "className": "filter-group"}),
                 html.h3({}, "Link Filters"),
                 html.div({"id": "link-filter-group", "className": "filter-group"},
                          html.label({},
                                     html.input({"type": "checkbox", "data-link-type": "Ethernet", "checked": True}),
                                     " Ethernet"),
                          html.label({}, html.input({"type": "checkbox", "data-link-type": "DAC", "checked": True}),
                                     " DAC"),
                          html.label({}, html.input({"type": "checkbox", "data-link-type": "AOC", "checked": True}),
                                     " AOC"),
                          html.label({}, html.input({"type": "checkbox", "data-link-type": "Fibre", "checked": True}),
                                     " Fibre"),
                          html.label({},
                                     html.input({"type": "checkbox", "data-link-type": "Wireless", "checked": True}),
                                     " Wireless"),
                          html.label({}, html.input({"type": "checkbox", "data-link-type": "VPN", "checked": True}),
                                     " VPN"),
                          html.label({}, html.input({"type": "checkbox", "data-link-type": "VLAN", "checked": True}),
                                     " VLAN"),
                          html.label({}, html.input(
                              {"type": "checkbox", "data-link-type": "IP-IP Tunnel", "checked": True}),
                                     " IP-IP Tunnel"),
                          html.label({}, html.input(
                              {"type": "checkbox", "data-link-type": "IP Sec Tunnel", "checked": True}),
                                     " IP Sec Tunnel"),
                          html.label({}, html.input({"type": "checkbox", "data-link-type": "Routed", "checked": True}),
                                     " Routed")),
                 html.h3({}, "Actions"),
                 html.button({"id": "add-link-btn", "className": "toolbar-button",
                              "on_click": (lambda e: on_toggle_link() if on_toggle_link else None)}, "🔗 Add Link"),
                 html.button({"id": "export-jpg-btn", "className": "toolbar-button"}, "🖼️ Export as JPG"),
                 html.button({"id": "export-json-btn", "className": "toolbar-button"}, "📤 Export Schematic"),
                 html.label({"htmlFor": "import-file", "id": "import-btn", "className": "toolbar-button"},
                            "📥 Import Schematic"),
                 html.input({"type": "file", "id": "import-file", "accept": ".json", "style": {"display": "none"}}),
                 html.button({"id": "new-schematic-btn", "className": "toolbar-button"}, "📄 New Schematic")))


DEVICE_CATALOGUE = {
    "Routers": [
        {"type": "Router", "model": "MikroTik hEX 5 Port Gigabit Desktop Router | E50UG", "ports": 5,
         "display": "MikroTik hEX 5 Port"},
        {"type": "Router", "model": "MikroTik hEX S 5 Port Gigabit 1x 2.5G SFP Desktop Router | E60iUGS", "ports": 6,
         "display": "MikroTik hEX S 6 Port"},
        {"type": "Router", "model": "MikroTik 10 Port Gigabit 1SFP+ 4 Core L5 Rack-Mount Router | RB4011iGS+RM",
         "ports": 11, "display": "MikroTik RB4011 11 Port"},
        {"type": "Router", "model": "MikroTik 8 Gigabit 1x2.5Gbps SFP Dual Core Router | L009UiGS-RM", "ports": 9,
         "display": "MikroTik L009 9 Port"}
    ],
    "Switches": [
        {"type": "Switch", "model": "MikroTik Cloud Router Switch 8 Port PoE 4SFP | CRS112-8P-4S-IN", "ports": 12,
         "display": "MikroTik CRS112 12 Port"},
        {"type": "Switch", "model": "MikroTik SwOS Cloud Smart Switch 24 Port Gigabit 2SFP+ | CSS326-24G-2S+RM",
         "ports": 26, "display": "MikroTik CSS326 26 Port"},
        {"type": "Switch", "model": "MikroTik Cloud Router Switch 24 Port Gigabit 2SFP+ | CRS326-24G-2S+RM",
         "ports": 26, "display": "MikroTik CRS326 26 Port"},
        {"type": "Switch", "model": "MikroTik Cloud Router Switch 24 Port PoE 450W 4SFP+| CRS328-24P-4S+RM",
         "ports": 28, "display": "MikroTik CRS328 28 Port"},
        {"type": "Switch", "model": "Netgear GS724PTT with 26 Ports", "ports": 26,
         "display": "Netgear GS724PTT 26 Port"}
    ],
    "Access Points": [
        {"type": "AP", "model": "MikroTik NetMetal 5SHP AC 1SFP Outdoor WiFi Router | RB922UAGS-5HPacD-NM", "ports": 3,
         "display": "MikroTik NetMetal 5SHP"},
        {"type": "AP", "model": "MikroTik OmniTIK 5ac 7.5dBi PoE Outdoor WiFi Omni AP | RBOmniTikPG-5HacD", "ports": 8,
         "display": "MikroTik OmniTIK 5ac"},
        {"type": "AP", "model": "MikroTik LHG 60GHz PtP CPE | RBLHGG-60ad", "ports": 2,
         "display": "MikroTik LHG 60GHz"},
        {"type": "AP", "model": "MikroTik LHG 5 24.5 PtP CPE | RBLHG5", "ports": 2, "display": "MikroTik LHG 5"},
        {"type": "AP", "model": "MikroTik LHG XL HP5 27dBi PtP | RBLHG-5HPnD-XL", "ports": 2,
         "display": "MikroTik LHG XL HP5"},
        {"type": "AP", "model": "MikroTik SXTsq 5 ac 16dBi Dual Chain Outdoor CPE | RBSXTsqG-5acD", "ports": 2,
         "display": "MikroTik SXTsq 5 ac"},
        {"type": "AP", "model": "Ubiquiti UISP airMAX Loco AC 5GHz 13dBi Radio | LOCO5AC", "ports": 2,
         "display": "Ubiquiti Loco AC 5GHz"},
        {"type": "AP", "model": "Ubiquiti UISP airMAX PowerBeam AC 5GHz 25dBi Radio | PBE-5AC-Gen2", "ports": 2,
         "display": "Ubiquiti PowerBeam AC"}
    ],
    "Servers": [
        {"type": "Server", "model": "Dell Poweredge R320", "ports": 5, "display": "Dell Poweredge R320"},
        {"type": "Server", "model": "Dell Poweredge R710", "ports": 5, "display": "Dell Poweredge R710"},
        {"type": "Server", "model": "Dell Poweredge R720", "ports": 5, "display": "Dell Poweredge R720"},
        {"type": "Server", "model": "Dell Poweredge R580", "ports": 5, "display": "Dell Poweredge R580"},
        {"type": "Server", "model": "HP Proliant DL380 Gen 8", "ports": 5, "display": "HP Proliant DL380 G8"},
        {"type": "Server", "model": "Supermicro NAS", "ports": 3, "display": "Supermicro NAS"}
    ],
    "Recorders": [
        {"type": "NVR", "model": "Hikvision DS-7608NXI-I2/8P/S", "ports": 1, "display": "Hikvision NVR 7608"},
        {"type": "NVR", "model": "Hikvision DS-7616NXI-I2/16P/S", "ports": 1, "display": "Hikvision NVR 7616"},
        {"type": "NVR", "model": "Dahua DHI-NVR4116HS-8P-4KS3", "ports": 1, "display": "Dahua NVR 4116"},
        {"type": "DVR", "model": "Hikvision iDS-7116HQHI-M1/T", "ports": 1, "display": "Hikvision DVR 7116"},
        {"type": "DVR", "model": "Hikvision iDS-7108HQHI-M1/T", "ports": 1, "display": "Hikvision DVR 7108"}
    ],
    "Other": [
        {"type": "Firewall", "model": "Fortinet Fortigate", "ports": 4, "display": "Fortinet Fortigate"},
        {"type": "ONT", "model": "Calix Gigabit ONT", "ports": 1, "display": "Calix Gigabit ONT"},
        {"type": "ONT", "model": "Cisco ONT", "ports": 8, "display": "Cisco ONT"},
        {"type": "Fibre", "model": "Fibre Splice", "ports": 0, "display": "Fibre Splice"}
    ]
}


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
                             html.button({"className": "add-device-btn", "on_click": add_device}, "+")))


@component
def DeviceCategory(category_name, devices, on_add_device=None):
    return html.details({"open": True},
                        html.summary(category_name),
                        *[CatalogueItem(device, on_add_device) for device in devices])


@component
def DeviceCatalogue(on_add_device=None):
    return html.div({"className": "device-catalogue"},
                    *[DeviceCategory(category_name, devices, on_add_device) for category_name, devices in
                      DEVICE_CATALOGUE.items()])


@component
def ThemeSwitcher(children):
    return html.div({"className": "theme-wrapper"}, children)


from reactpy import component, html, hooks, use_state


@component
def PortItem(port, device_id, on_update_port=None, on_remove_port=None, on_add_port=None):
    from reactpy import html

    # Local state for this port
    name, set_name = use_state(port.get("name", ""))
    ips, set_ips = use_state(list(port.get("ips", [])))
    vlans, set_vlans = use_state(list(port.get("vlans", [])))
    bridge, set_bridge = use_state(port.get("bridge", ""))
    ip_input, set_ip_input = use_state("")
    vlan_input, set_vlan_input = use_state("")
    is_open, set_open = use_state("False")

    # Handlers
    def handle_name_change(e):
        set_name(e['target']['value'])
        if on_update_port:
            on_update_port(port['id'], {"name": e['target']['value']})

    def handle_bridge_change(e):
        set_bridge(e['target']['value'])
        if on_update_port:
            on_update_port(port['id'], {"bridge": e['target']['value']})

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
            if on_update_port:
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
                            html.details({"open": False, "onclick": handle_open},
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
                                                 html.option({"value": ""}, "(None)")
                                             ),
                                             html.hr({"style": {"borderColor": "#444"}}),
                                             html.label({}, "IP Addresses (Untagged)"),
                                             html.div({"className": "port-ip-list"}, *[html.div({}, ip) for ip in ips]),
                                             html.input({
                                                 "type": "text",
                                                 "placeholder": "Add IP/Mask",
                                                 "value": ip_input,
                                                 "on_change": lambda e: set_ip_input(e['target']['value'])
                                             }),
                                             html.button({
                                                 "className": "prop-button small info add-ip-btn",
                                                 "on_click": lambda e: add_ip(ip_input) or set_ip_input("")
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
                                                 "on_click": lambda e: add_vlan(vlan_input) or set_vlan_input("")
                                             }, "Add VLAN"),
                                             html.hr({"style": {"borderColor": "#444"}}),
                                             html.button({
                                                 "className": "prop-button danger remove-port-btn",
                                                 "on_click": remove_port
                                             }, "Remove Port")
                                             )
                                    )
                            ),
                    html.button({
                        "id": "add-port-btn",
                        "className": "prop-button",
                        "on_click": add_port_click
                    }, "Add Port")
                    )

    # ---------------- Bridges Panel ----------------


@component
def BridgesPanel(bridges, on_add_bridge, on_update_bridge, on_remove_bridge):
    return html.div({"className": "prop-group"},
                    html.label({}, "Bridges"),
                    html.ul({},
                            *[

                             html.details({"open": False, "key": b["id"]},
                                html.summary({"className": "bridge-header"}, b["name"]),
                                        html.div({"className": "bridge-details"},
                                                 html.label({}, "Name"),
                                                 html.input({
                                                     "type": "text",
                                                     "value": b["name"],
                                                     "on_change": lambda e, bid=b["id"]: on_update_bridge(bid, {
                                                         "name": e['target']['value']})
                                                 }),
                                                 html.label({}, "Member Ports"),
                                                 html.ul({}, *[
                                                     html.li({}, port) for port in b.get("ports", [])
                                                 ]),
                                                 html.button({
                                                     "className": "prop-button danger small",
                                                     "on_click": lambda e, bid=b["id"]: on_remove_bridge(bid)
                                                 }, "Remove Bridge")
                                                 )
                                        )
                                for b in bridges
                            ]
                            ),
                    html.button({
                        "id": "add-bridge-btn",
                        "className": "prop-button",
                        "on_click": lambda e: on_add_bridge()
                    }, "Add Bridge")
                    )


# ---------------- Services Panel (VPNs / Tunnels) ----------------
@component
def ServicesPanel(title, services, service_type, on_add_service, on_update_service, on_remove_service):
    return html.div({"className": "prop-group"},
                    html.label({}, title),
                    html.ul({},
                            *[
                                html.li({"className": "service-item expanded", "key": s["id"]},
                                        html.div({"className": "service-header"},
                                                 html.strong({}, f"{s['name']} ({service_type.upper()})"),
                                                 html.span({}, "▼")
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
                                                     "on_click": lambda e, sid=s["id"]: on_remove_service(sid)
                                                 }, f"Remove {service_type.upper()}")
                                                 )
                                        )
                                for s in services
                            ]
                            ),
                    html.button({
                        "id": f"add-{service_type.lower()}-btn",
                        "className": "prop-button info",
                        "on_click": lambda e: on_add_service()
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

    def add_device(item):
        # normalize ports
        ports_list = []
        ports = item.get("ports", [])
        if isinstance(ports, int):
            ports_list = [
                {"id": f"port{i}", "name": f"ether{i}", "ips": [], "vlans": [], "bridge": None}
                for i in range(1, ports + 1)
            ]
        elif isinstance(ports, list):
            ports_list = [
                p if isinstance(p, dict) else {"id": f"port{i}", "name": str(p), "ips": [], "vlans": [], "bridge": None}
                for i, p in enumerate(ports, start=1)
            ]

        new_device = {
            "id": f"dev{len(devices) + 1}",
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

        devices.append(new_device)
        set_devices(devices[:])  # force re-render

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

    def remove_device_property(dev_id, prop_type, item_id):
        updated = []
        for d in devices:
            if d['id'] == dev_id:
                dn = dict(d)
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
                              "ports": []}
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

    def add_port_to_device(dev_id):
        updated = []
        for d in devices:
            if d['id'] == dev_id:
                ports = list(d['ports'])
                pid = f"port-{dev_id}-{len(ports) + 1}"
                ports.append({
                    "id": pid,
                    "name": f"ether{len(ports) + 1}",
                    "ips": [],
                    "vlans": [],
                    "bridge": None
                })
                updated.append({**d, "ports": ports})
            else:
                updated.append(d)
        set_devices(updated)

    def confirm_create_link(link_type):
        s = dict(linking)
        if not s.get('start') or not s.get('end'):
            return
        lid = f"link-{len(links)}"
        new_link = {'id': lid, 'sourceDeviceId': s['start']['deviceId'], 'sourcePortId': s['start']['portId'],
                    'targetDeviceId': s['end']['deviceId'], 'targetPortId': s['end']['portId'], 'linkType': link_type,
                    'color': '#99cc00', 'ips': []}
        set_links(links + [new_link])
        set_linking({'active': False, 'start': None, 'end': None, 'show_modal': False})

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
        except Exception:
            # ignore invalid JSON for now
            pass

    # build UI
    header = html.div({"className": "header"},
                      html.img({"src": "https://placehold.co/100x40/000000/99cc00?text=Logo", "alt": "Logo"}),
                      "Next Level Networks - Network Planning Tool")

    # toolbar/sidebar
    sidebar = Sidebar(on_add_device=add_device, on_toggle_link=on_toggle_link, linking_active=linking['active'])

    # canvas
    svg_children = []
    # compute simple straight-line links
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

        # simple grid inside device box
        def port_pos(device, idx):
            cols = 4
            cell_w = 70 / cols
            cell_h = 70 / 4
            col = idx % cols
            row = idx // cols
            x = device['x'] + col * cell_w + cell_w / 2
            y = device['y'] + row * cell_h + cell_h / 2
            return x, y

        x1, y1 = port_pos(src, s_idx)
        x2, y2 = port_pos(tgt, t_idx)
        path = f"M {x1} {y1} L {x2} {y2}"
        svg_children.append(
            html.raw(f'<path d="{path}" stroke="{l.get("color", "#fff")}" stroke-width="3" fill="none" />'))

    svg = html.svg({"width": "100%", "height": "100%", "style": {"position": "absolute", "top": "0", "left": "0"}},
                   *svg_children)

    device_elements = []
    for d in devices:
        # ports
        port_buttons = []
        cols = 4
        rows = (len(d['ports']) + cols - 1) // cols  # dynamic rows
        for i, p in enumerate(d['ports']):
            port_id = p['id']  # capture correctly
            dev_id = d['id']
            port_buttons.append(
                html.button(
                    {"className": "visual-port",
                     "style": {"width": "16px", "height": "16px", "borderRadius": "50%", "margin": "2px"},
                     "on_click": lambda e, did=dev_id, pid=port_id: port_clicked(did, pid)},
                    str(i + 1)
                )
            )
        dev_style = {"position": "absolute", "left": f"{d['x']}px", "top": f"{d['y']}px", "width": "70px",
                     "height": "70px", "borderRadius": "8px", "backgroundColor": "#2b2b2b",
                     "border": "2px solid #676767", "display": "flex", "flexDirection": "column",
                     "alignItems": "center", "justifyContent": "center", "cursor": "grab"}

        # mouse down handler to start drag
        dev_el = html.div({"id": d['id'], "className": "device", "style": dev_style,
                           "on_mouse_down": (lambda e, did=d['id']: on_device_mouse_down(did, e)),
                           "on_click": (lambda e, did=d['id']: select_device(did))}, html.div(
            {"className": "device-ports-container",
             "style": {"display": "grid", "gridTemplateColumns": "repeat(4, 1fr)", "gridTemplateRows": "repeat(4, 1fr)",
                       "width": "100%", "height": "100%", "position": "absolute", "top": "0", "left": "0",
                       "padding": "2px", "boxSizing": "border-box"}}, *port_buttons), html.div(
            {"className": "device-label",
             "style": {"position": "absolute", "bottom": "2px", "fontSize": "10px", "background": "rgba(0,0,0,0.5)",
                       "padding": "2px 4px", "borderRadius": "3px"}}, d['name']))
        device_elements.append(dev_el)

    canvas = html.div({"id": "canvas", "style": {"position": "relative", "flexGrow": 1, "backgroundColor": "#000",
                                                 "backgroundImage": "linear-gradient(#676767 1px, transparent 1px), linear-gradient(90deg, #676767 1px, transparent 1px)",
                                                 "backgroundSize": "25px 25px", "overflow": "hidden"},
                       "on_mouse_move": on_canvas_mouse_move, "on_mouse_up": on_canvas_mouse_up}, svg, *device_elements)

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
                    on_update_port=lambda port_id, updated: set_devices([
                        dict(d) if d['id'] != sel['id'] else dict({
                            **d,
                            "ports": [
                                dict(port) if port['id'] != port_id else dict({**port, **updated})
                                for port in d['ports']
                            ]
                        }) for d in devices
                    ]),
                    on_remove_port=lambda port_id: set_devices([
                        dict(d) if d['id'] != sel['id'] else dict({
                            **d,
                            "ports": [port for port in d['ports'] if port['id'] != port_id]
                        }) for d in devices
                    ]),
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
                                                   "on_click": (lambda lt=lt: confirm_create_link(lt))}, lt) for lt in
                                      ["Ethernet", "Fibre", "VPN", "VLAN", "Routed"]]),
                                       html.div({"style": {"marginTop": "8px"}}, html.button(
                                           {"className": "prop-button danger",
                                            "on_click": lambda ev: cancel_link_modal()}, "Cancel"))))

    # export/import UI
    export_ui = html.div({"style": {"padding": "10px"}}, html.h3({}, "Export / Import JSON"),
                         html.button({"on_click": lambda e: prepare_export()}, "Prepare Export"), html.div({},
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
                         html.button({"on_click": lambda e: load_import_text()}, "Load from text"))

    return ThemeSwitcher(
        html.div({"className": "dashboard", "style": {"display": "flex", "flexDirection": "column", "height": "100vh"}},
                 header,
                 html.div({"className": "main-container", "style": {"display": "flex", "flex": 1}}, sidebar, canvas,
                          properties_panel), link_modal, export_ui))
