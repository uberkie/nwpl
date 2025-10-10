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
    selected, set_selected = use_state((devices[0].name if devices else ""))
    port_selected, set_port_selected = use_state("")
    new_port_ip, set_new_port_ip = use_state("")

    def append(line):
        set_output(output + [line])

    def run_command(e=None):
        c = cmd.strip()
        if not c:
            return
        append(f"> {c}")
        parts = c.split()
        if parts[0] == "ping" and len(parts) >= 3:
            src = parts[1]
            dst = parts[2]
            dev = None
            if simulator and devices:
                for d in devices:
                    if d.name == selected:
                        dev = d
                        break
            if dev is None:
                append("Error: no device selected or device not found")
            else:
                # allow overriding src with selected port IP
                if port_selected:
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
            dev = None
            if simulator and devices:
                for d in devices:
                    if d.name == selected:
                        dev = d
                        break
            if dev is None:
                append("Error: no device selected or device not found")
            else:
                path = dev.traceroute(src, dst, simulator)
                append(f"traceroute: {path}")
        else:
            append("Unknown command. Use: ping <src_ip> <dst_ip> or traceroute <src_ip> <dst_ip>")
        set_cmd("")

    def handle_input(e):
        set_cmd(e['target']['value'])

    def refresh_ports():
        # Ensure port_selected reflects current device's first port (showing iftype and IP or 'unassigned')
        if not devices:
            set_port_selected("")
            return
        for d in devices:
            if d.name == selected:
                ports = []
                for p in getattr(d, 'ports', []):
                    ipstr = getattr(p, 'ip_interface', None)
                    if ipstr:
                        ipval = str(ipstr.ip)
                    else:
                        ipval = 'unassigned'
                    ports.append(f"{p.iftype}:{ipval}")
                if ports:
                    set_port_selected(ports[0])
                else:
                    set_port_selected("")
                return

    def add_port_to_device(e=None):
        if not simulator:
            append("No simulator provided to add a port")
            return
        if not new_port_ip:
            append("Provide IP/Mask for new port (e.g. 192.0.2.10/24)")
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
            append(f"Added port {p.id} {new_port_ip} to {dev.name}")
            set_new_port_ip("")
            refresh_ports()
        except Exception as exc:
            append(f"Failed to add port: {exc}")

    # Render
    return html.div({"className": "sim-terminal", "style": {"display": "flex", "flexDirection": "column", "height": "100%"}},
                    html.div({"style": {"flex": "1", "overflowY": "auto", "background": "#111", "color": "#eee", "padding": "8px"}},
                             *[html.div({}, line) for line in output]
                    ),
                    html.div({"style": {"display": "flex", "gap": "8px", "padding": "8px"}},
                             html.select({"value": selected, "on_change": lambda e: set_selected(e['target']['value'])},
                                         *([html.option({"value": d.name}, d.name) for d in (devices or [])])
                             ),
                             html.input({"type": "text", "value": cmd, "on_change": handle_input, "style": {"flex": "1"}}),
                             html.button({"onClick": run_command}, "Run")
                    )
                    )
