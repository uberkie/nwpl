from reactpy import component, html, hooks, use_state, event
import asyncio
from asgiref.sync import sync_to_async
from ._notifier import notify

# Small admin UI to manage device models stored in the Django ORM
@component
def DeviceModelsAdmin():
    from planning.models import DeviceModel

    # load models from DB
    models_list, set_models_list = use_state([])
    model_value, set_model_value = use_state("")
    display, set_display = use_state("")
    mtype, set_type = use_state("")
    ports, set_ports = use_state(0)
    category, set_category = use_state("")
    # fixed allowed categories for the admin UI (lowercase canonical values)
    category_options, set_category_options = use_state(["router", "switch", "access point", "server", "recorder", "cctv", "other"])
    type_options, set_type_options = use_state([])

    async def load():
        # Run ORM calls in a thread to avoid SynchronousOnlyOperation in async context
        qs = await sync_to_async(list, thread_sensitive=True)(DeviceModel.objects.all().order_by('category', 'display'))
        set_models_list(qs)
        # keep type options dynamic, but category choices are fixed by project convention
        set_type_options(sorted({m.type for m in qs if getattr(m, 'type', None)}))

    
    @event
    async def add_model(e=None):
        from planning.models import DeviceModel
        display_name = display or model_value or mtype

        # create model in DB on a worker thread
        await sync_to_async(DeviceModel.objects.create, thread_sensitive=True)(
            category=category or "other",
            type=mtype,
            model=model_value,
            ports=int(ports or 0),
            display=display_name,
        )

        # refresh list and type options
        await load()
        # notify listeners (catalogue) to reload immediately
        try:
            notify()
        except Exception:
            pass
        set_model_value("")
        set_display("")
        set_type("")
        set_ports(0)
        set_category("")

    def remove_model(mid):
        # run deletion asynchronously so button handlers remain responsive
        from asgiref.sync import sync_to_async

        async def _del():
            try:
                # delete the object
                await sync_to_async(DeviceModel.objects.filter(id=mid).delete, thread_sensitive=True)()
            except Exception:
                pass
            # refresh list in main context
            await load()
            # notify listeners after delete
            try:
                notify()
            except Exception:
                pass

        import asyncio
        asyncio.create_task(_del())

    # initial load - schedule the async loader to avoid running sync ORM in the effect
    def _start_load():
        asyncio.create_task(load())

    hooks.use_effect(lambda: _start_load(), [])

    return html.div({"className": "device-models-admin"},
                    html.h4({}, "Device Models (DB)"),
                    html.ul({}, *[html.li({"key": m.id}, f"{m.category} / {m.display or m.model} ({m.ports} ports)", html.button({"onClick": (lambda e, mid=m.id: remove_model(mid)), "style": {"marginLeft": "8px"}}, "Remove")) for m in models_list]),
                    html.div({"style": {"marginTop": "8px"}},
                             html.label({}, "Category (router|switch|access point|server|recorder|cctv|other)"),
                             html.select({"value": category, "on_change": lambda e: set_category(e['target']['value'])},
                                         html.option({"value": ""}, "(select or enter...)"),
                                         *[html.option({"value": opt}, opt.title() if opt != 'cctv' else opt.upper()) for opt in category_options]
                                         ),
                             html.label({}, "Model (type identifier)"),
                             html.input({"type": "text", "placeholder": "Model (eg. RB4011iGS+RM)", "value": model_value, "on_change": lambda e: set_model_value(e['target']['value'])}),
                             html.label({}, "Type (device class)") ,
                             html.select({"value": mtype, "on_change": lambda e: set_type(e['target']['value'])},
                                         html.option({"value": ""}, "(select or enter...)"),
                                         *[html.option({"value": opt}, opt) for opt in type_options]
                                         ),
                             html.label({}, "Ports"),
                             html.input({"type": "number", "placeholder": "Ports", "value": ports, "on_change": lambda e: set_ports(e['target']['value'])}),
                             html.label({}, "Display Name"),
                             html.input({"type": "text", "placeholder": "Display Name (friendly)", "value": display, "on_change": lambda e: set_display(e['target']['value'])}),
                             html.button({"onClick": add_model, "style": {"marginLeft": "6px"}}, "Add Model")
                             )
                    )
