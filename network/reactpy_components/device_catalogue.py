from reactpy import component, html, hooks
import asyncio
from asgiref.sync import sync_to_async
from ._notifier import subscribe

# Define your device catalogue data (fallback). Do NOT query the ORM at import
# time because ReactPy runs in an async context and that triggers
# SynchronousOnlyOperation. The live DB loader inside the component will
# fetch rows using sync_to_async.
DEVICE_CATALOGUE = {}


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

    # Use a single async effect that runs the loader and then polls.
    poll_interval = 5.0  # seconds

    async def _effect_poller():
        # initial load
        await load_from_db()
        try:
            while True:
                await asyncio.sleep(poll_interval)
                await load_from_db()
        except asyncio.CancelledError:
            # cleanup when component unmounts
            return

    # ReactPy's hooks.use_effect accepts an async function; pass the poller directly.
    # Also subscribe to the in-process notifier so creates/deletes trigger an
    # immediate reload.
    def _subscribe_and_run():
        # subscribe returns an unsubscribe callable
        unsub = subscribe(lambda: asyncio.create_task(load_from_db()))
        # return unsubscribe so the effect cleanup will remove subscriber
        return unsub

    hooks.use_effect(_effect_poller, [])
    hooks.use_effect(_subscribe_and_run, [])

    return html.div({"className": "device-catalogue"},
                    *[DeviceCategory(category_name, devices, on_add_device) for category_name, devices in
                      (data.items() if isinstance(data, dict) else [])]
                    )


def run_catalogue_load_for_tests():
    """Development helper: run the same DB->mapping transformation synchronously and return the mapping.

    Use from manage.py shell for quick verification that DB rows map to the UI groups.
    """
    from planning.models import DeviceModel

    qs = list(DeviceModel.objects.all().order_by('category', 'display'))
    mapping = {}
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

    return mapping
