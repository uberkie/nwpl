from reactpy import component, html, hooks, use_state


@component
def SimTerminal(simulator=None, devices=None):
    """A minimal server-side terminal UI for the NetworkSimulator.

    Props:
    - simulator: NetworkSimulator instance (passed from server code)
    - devices: list of Device objects (simulator.devices)
    """
    output, set_output = use_state([])
    cmd, set_cmd = use_state("")
    selected, set_selected = use_state("")
    port_selected, set_port_selected = use_state("")
    new_port_ip, set_new_port_ip = use_state("")

    # initialize selected device when devices prop arrives/changes
    hooks.use_effect(lambda: (set_selected(devices[0].name) if devices and not selected else None), [devices])

    def append(line):
        set_output(output + [line])

    def run_command(e=None):
        c = cmd.strip()
        if not c:
            return
        append(f"> {c}")
        parts = c.split()
        # Find selected device object
        dev = None
        if simulator and devices:
            for d in devices:
                if d.name == selected:
                    dev = d
                    break

        if parts[0] == "ping" and len(parts) >= 3:
            src = parts[1]
            dst = parts[2]
            if dev is None:
                append("Error: no device selected or device not found")
            else:
                # allow overriding src with selected port IP (port_selected stores IP or special marker)
                if port_selected and port_selected != '__unassigned__':
                    src_ip = port_selected
                else:
                    src_ip = src
                ok, trace = dev.ping(src_ip, dst, simulator)
                append(f"ok: {ok}")
                for t in trace:
                    append(str(t))
        elif parts[0] == "traceroute" and len(parts) >= 3:
            src = parts[1]
            dst = parts[2]
            if dev is None:
                append("Error: no device selected or device not found")
            else:
                # prefer selected port IP when present
                if port_selected and port_selected != '__unassigned__':
                    src_ip = port_selected
                else:
                    src_ip = src
                path = dev.traceroute(src_ip, dst, simulator)
                append(f"traceroute: {path}")
        else:
            append("Unknown command. Use: ping <src_ip> <dst_ip> or traceroute <src_ip> <dst_ip>")
        set_cmd("")

    def handle_input(e):
        set_cmd(e['target']['value'])

    def refresh_ports():
        # Build list of port option tuples (value, label). value is IP string or '__unassigned__'
        if not devices:
            set_port_selected("")
            return []
        for d in devices:
            if d.name == selected:
                opts = []
                for p in getattr(d, 'ports', []):
                    ipif = getattr(p, 'ip_interface', None)
                    if ipif:
                        ipval = str(ipif.ip)
                        opts.append((ipval, f"{p.iftype}:{ipval}"))
                    else:
                        opts.append(('__unassigned__', f"{p.iftype}:unassigned"))
                # choose the first with a real IP, otherwise first option, otherwise blank
                chosen = ''
                for v, _ in opts:
                    if v != '__unassigned__':
                        chosen = v
                        break
                if not chosen and opts:
                    chosen = opts[0][0]
                set_port_selected(chosen)
                return opts
        return []

    def add_port_to_device(e=None):
        if not simulator:
            append("No simulator provided to add a port")
            return
        if not new_port_ip:
            append("Provide IP/Mask for new port (e.g. 192.0.2.10/24) or iftype:ip/prefix")
            return
        # find device
        dev = None
        for d in devices or []:
            if d.name == selected:
                dev = d
                break
        if not dev:
            append("Device not found")
            return
        try:
            # allow format 'iftype:ip/prefix' (e.g. 'ethernet:192.0.2.10/24')
            if ':' in new_port_ip:
                iftype, ipstr = new_port_ip.split(':', 1)
            else:
                iftype, ipstr = 'ethernet', new_port_ip
            p = dev.add_port(f"p{len(dev.ports)+1}", ipstr)
            p.iftype = iftype
            append(f"Added port {p.id} {iftype}:{ipstr} to {dev.name}")
            set_new_port_ip("")
            refresh_ports()
        except Exception as exc:
            append(f"Failed to add port: {exc}")

    # ensure ports refresh when selected device or devices list change
    hooks.use_effect(lambda: refresh_ports(), [selected, devices])

    # Render
    port_options = refresh_ports() or []
    return html.div({"className": "sim-terminal", "style": {"display": "flex", "flexDirection": "column", "height": "100%"}},
                    html.div({"style": {"flex": "1", "overflowY": "auto", "background": "#111", "color": "#eee", "padding": "8px"}},
                             *[html.div({}, line) for line in output]
                    ),
                    html.div({"style": {"display": "flex", "gap": "8px", "padding": "8px", "alignItems": "center"}},
                             # device selector
                             html.select({"value": selected, "on_change": lambda e: set_selected(e['target']['value'])},
                                         *([html.option({"value": d.name}, d.name) for d in (devices or [])])
                             ),
                             # port selector
                             html.select({"value": port_selected, "on_change": lambda e: set_port_selected(e['target']['value'])},
                                         *([html.option({"value": v}, label) for v, label in port_options])
                             ),
                             html.input({"type": "text", "value": cmd, "on_change": handle_input, "style": {"flex": "1"}}),
                             html.button({"onClick": run_command}, "Run"),
                             # add port input
                             html.input({"type": "text", "value": new_port_ip, "placeholder": "iftype:ip/prefix", "on_change": lambda e: set_new_port_ip(e['target']['value']), "style": {"width": "220px"}}),
                             html.button({"onClick": add_port_to_device}, "Add Port")
                    )
                    )
