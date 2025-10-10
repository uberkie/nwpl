from reactpy import component, html, hooks
import asyncio
from asgiref.sync import sync_to_async

# Define your device catalogue data (fallback)
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
        """Load DeviceModel rows in a thread and update component state."""
        try:
            from planning.models import DeviceModel
            qs = await sync_to_async(list, thread_sensitive=True)(DeviceModel.objects.all().order_by('category', 'display'))
        except Exception as e:
            print("DeviceCatalogue: DB load error:", e)
            return

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

        try:
            print(f"DeviceCatalogue: loaded {len(qs)} rows, categories={list(mapping.keys())}")
        except Exception:
            pass

        # update UI state (replace fallback even if mapping empty)
        set_data(mapping)

    async def _receive_event(message):
        # Called when a Channels message arrives (cross-process)
        try:
            await load_from_db()
        except Exception:
            pass

    # Register channel layer listener (hook). If unavailable, it's ignored.
    try:
        hooks.use_channel_layer("chat_general", receiver=_receive_event)
    except Exception:
        pass

    # On mount: load initial DB data and subscribe to in-process notifier
    def _mount():
        asyncio.create_task(load_from_db())

        try:
            from reactpy_components import _notifier

            def _on_notify():
                try:
                    asyncio.create_task(load_from_db())
                except Exception:
                    pass

            unsubscribe = _notifier.subscribe(_on_notify)

            def _cleanup():
                try:
                    if callable(unsubscribe):
                        unsubscribe()
                except Exception:
                    pass

            return _cleanup
        except Exception:
            return None

    hooks.use_effect(_mount, [])

    return html.div({"className": "device-catalogue"},
                    *[DeviceCategory(category_name, devices, on_add_device) for category_name, devices in
                      (data.items() if isinstance(data, dict) else [])]
                    )


def run_catalogue_load_for_tests():
    """Synchronous helper to load the catalogue mapping from the DB.

    Useful from `manage.py shell` for debugging without mounting the ReactPy component.
    Returns a mapping: category -> list[device dict]
    """
    try:
        from planning.models import DeviceModel
        qs = list(DeviceModel.objects.all().order_by('category', 'display'))
    except Exception:
        return {}

    category_map = {
        "router": "Routers",
        "switch": "Switches",
        "access point": "Access Points",
        "server": "Servers",
        "recorder": "Recorders",
        "cctv": "Other",
        "other": "Other",
    }

    mapping = {}
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


def seed_db_from_fallback():
    """Idempotently seed the DeviceModel table from DEVICE_CATALOGUE fallback data.

    Matches on (category, model, display) to avoid duplicates.
    Returns the number of records created.
    """
    try:
        from planning.models import DeviceModel
    except Exception:
        return 0

    created = 0
    for cat, devices in DEVICE_CATALOGUE.items():
        for d in devices:
            model = d.get('model')
            display = d.get('display')
            ports = d.get('ports', 0)
            dtype = d.get('type', '')
            # check existence by model+display (case-insensitive) to avoid duplicates
            if not DeviceModel.objects.filter(model__iexact=model, display__iexact=display).exists():
                DeviceModel.objects.create(category=cat, type=dtype, model=model, ports=ports, display=display)
                created += 1

    return created
