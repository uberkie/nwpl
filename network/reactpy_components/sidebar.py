from reactpy import component, html, hooks, use_state


@component
def Sidebar():
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
            return bool(e.get('checked', False)) if isinstance(e, dict) else False
        except Exception:
            return False

    return html.div(
        {"className": "sidebar"},
        html.div({"className": "header"},
                 html.img(
                     {"src": "https://placehold.co/100x40/000000/99cc00?text=Logo", "alt": "Next Level Networks Logo"}),
                 "Next Level Networks - Network Planning Tool"
                 ),
        html.div({"className": "toolbar"},
                 html.h3({}, "Device Catalogue"),
                 html.div({"className": "device-catalogue"}, ""),
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
                                     " Routed")
                          ),
                 html.h3({}, "Actions"),
                 html.button({"id": "add-link-btn", "className": "toolbar-button"}, "🔗 Add Link"),
                 html.button({"id": "export-jpg-btn", "className": "toolbar-button"}, "🖼️ Export as JPG"),
                 html.button({"id": "export-json-btn", "className": "toolbar-button"}, "📤 Export Schematic"),
                 html.label({"htmlFor": "import-file", "id": "import-btn", "className": "toolbar-button"},
                            "📥 Import Schematic"),
                 html.input({"type": "file", "id": "import-file", "accept": ".json", "style": {"display": "none"}}),
                 html.button({"id": "new-schematic-btn", "className": "toolbar-button"}, "📄 New Schematic")
                 )
    )
