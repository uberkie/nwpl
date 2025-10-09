from reactpy import component, html, use_state


@component
def Popup(devices):
    # visible = whether popup is open
    # active_device = which device was clicked
    visible, set_visible = use_state(False)
    active_device, set_active_device = use_state(None)

    def open_popup(device_name):
        def handler(event):
            set_active_device(device_name)
            set_visible(True)

        return handler

    def close_popup(event):
        set_visible(False)
        set_active_device(None)

    return html.div(
        {},
        # Render the device cards
        html.div(
            {"className": "devices"},
            [
                html.div(
                    {"className": "device", "on_click": open_popup(name)},
                    icon(),
                    html.span({"className": "device-label"}, name)
                )
                for name, icon in devices
            ]
        ),
        # The popup itself
        html.div(
            {"id": "popup", "className": f"popup {'active' if visible else ''}"},
            html.div(
                {"className": "popup-content"},
                html.span({"className": "popup-close", "on_click": close_popup}, "×"),
                html.h2({}, active_device if active_device else ""),
                html.p({}, f"Details for {active_device}" if active_device else "")
            )
        )
    )
