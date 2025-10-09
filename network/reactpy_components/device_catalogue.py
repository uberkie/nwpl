from reactpy import component, html, hooks
import asyncio
from asgiref.sync import sync_to_async

# Define your device catalogue data (fallback)
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
    name, set_name = hooks.use_state("")

    def add_device(e):
        if on_add_device:
            on_add_device({**device, "name": name})
            set_name("")

    return html.div({"className": "catalogue-item", "data-type": device["type"], "data-model": device["model"],
                     "data-ports": device["ports"]},
                    html.p(device.get("display") or device.get("model")),
                    html.div({"className": "controls"},
                             html.label(html.input({"type": "text", "placeholder": "Device Name", "value": name,
                                                    "on_change": lambda e: set_name(e['target']['value'])})),
                             html.button({"className": "add-device-btn", "on_click": add_device}, "+")
                             )
                    )


@component
def DeviceCategory(category_name, devices, on_add_device=None):
    return html.details({"open": True},
                        html.summary(category_name),
                        *[CatalogueItem(device, on_add_device) for device in devices]
                        )


@component
def DeviceCatalogue(on_add_device=None):
    # data state holds a mapping: category -> list[device dict]
    data, set_data = hooks.use_state(DEVICE_CATALOGUE)

    async def load_from_db():
        # lazy-load DeviceModel rows and convert to the catalogue shape
        from planning.models import DeviceModel
        qs = await sync_to_async(list, thread_sensitive=True)(DeviceModel.objects.all().order_by('category', 'display'))
        if not qs:
            return
        mapping = {}

        # map lower-case category values into the display groups used by DEVICE_CATALOGUE
        category_map = {
            "router": "Routers",
            "switch": "Switches",
            "access point": "Access Points",
            "server": "Servers",
            "recorder": "Recorders",
            "cctv": "Other",
            "other": "Other",
        }

        for m in qs:
            raw = (m.category or "other").strip().lower()
            cat = category_map.get(raw, raw.title())
            mapping.setdefault(cat, []).append({
                "type": m.type,
                "model": m.model,
                "ports": m.ports,
                "display": m.display,
            })

        # debug: print what we loaded so dev logs show entries
        try:
            print(f"DeviceCatalogue: loaded {len(qs)} rows, categories={list(mapping.keys())}")
        except Exception:
            pass

        # only update if we found DB entries
        if mapping:
            set_data(mapping)

    # Start an async poller that reloads the DB every few seconds so the
    # catalogue reflects newly-created devices without requiring a page reload.
    poll_interval = 5.0  # seconds

    poll_task = None

    async def _poller():
        # run an initial load first
        await load_from_db()
        try:
            while True:
                await asyncio.sleep(poll_interval)
                await load_from_db()
        except asyncio.CancelledError:
            # expected on cleanup
            return

    def _start_poller():
        nonlocal poll_task
        if poll_task is None or poll_task.done():
            poll_task = asyncio.create_task(_poller())

    def _stop_poller():
        nonlocal poll_task
        try:
            if poll_task is not None and not poll_task.done():
                poll_task.cancel()
        finally:
            poll_task = None

    # Start the poller when the component mounts, and cancel it on cleanup
    def _mount():
        _start_poller()
        return _stop_poller

    hooks.use_effect(_mount, [])

    return html.div({"className": "device-catalogue"},
                    *[DeviceCategory(category_name, devices, on_add_device) for category_name, devices in
                      (data.items() if isinstance(data, dict) else [])]
                    )
