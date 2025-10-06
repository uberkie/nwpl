from reactpy import component, html


@component
def DeviceGrid(devices):
    return html.div(
        {"className": "device-grid"},
        [html.div({"className": "device"}, device) for device in devices]
    )
