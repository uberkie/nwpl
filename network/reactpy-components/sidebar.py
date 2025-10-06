from reactpy import component, html, use_state


@component
def Sidebar():
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
