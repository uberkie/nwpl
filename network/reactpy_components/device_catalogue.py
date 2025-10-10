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

    # Start a single initial load when the component mounts. We rely on an
    # external notifier (Django signals -> in-process notifier) to trigger
    # subsequent reloads. Keeping a single initial load avoids running the
    # ORM at import time while ensuring the UI shows DB entries on mount.
    # Channel layer receiver: reload DB when a cross-process message arrives.
    async def _receive_event(message):
        # message payload may vary; we simply trigger a reload
        try:
            await load_from_db()
        except Exception:
            pass

    # register channel layer listener for cross-process notifications
    try:
        # use the ReactPy hook to subscribe to a channel layer group; the
        # project's signals send to group "chat_general" so we listen there.
        hooks.use_channel_layer("chat_general", receiver=_receive_event)
    except Exception:
        # hook may not be available in all environments — ignore
        pass

    def _mount():
        # schedule an async initial load
        asyncio.create_task(load_from_db())

        # also subscribe to optional in-process notifier so single-process
        # dev servers get immediate reloads without requiring the channel layer
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
