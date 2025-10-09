from reactpy import component, html, hooks, use_state

# Small admin UI to manage device models stored in the Django ORM
@component
def DeviceModelsAdmin():
    from nwpl.network.planning.models import DeviceModel

    # load models from DB
    models_list, set_models_list = use_state([])
    name, set_name = use_state("")
    mtype, set_type = use_state("")
    ports, set_ports = use_state(0)
    category, set_category = use_state("")

    def load():
        qs = list(DeviceModel.objects.all().order_by('category', 'display'))
        set_models_list(qs)

    def add_model(e=None):
        if not mtype:
            return
        dm = DeviceModel(category=category, type=mtype, model=name, ports=int(ports or 0), display=(name or mtype))
        dm.save()
        load()
        set_name("")
        set_type("")
        set_ports(0)
        set_category("")

    def remove_model(mid):
        try:
            dm = DeviceModel.objects.get(id=mid)
            dm.delete()
        except DeviceModel.DoesNotExist:
            pass
        load()

    # initial load
    hooks.use_effect(lambda: load(), [])

    return html.div({"className": "device-models-admin"},
                    html.h4({}, "Device Models (DB)"),
                    html.ul({}, *[html.li({"key": m.id}, f"{m.category} / {m.display} ({m.ports} ports)", html.button({"onClick": (lambda e, mid=m.id: remove_model(mid)), "style": {"marginLeft": "8px"}}, "Remove")) for m in models_list]),
                    html.div({"style": {"marginTop": "8px"}},
                             html.input({"type": "text", "placeholder": "Category", "value": category, "on_change": lambda e: set_category(e['target']['value'])}),
                             html.input({"type": "text", "placeholder": "Display Name", "value": name, "on_change": lambda e: set_name(e['target']['value'])}),
                             html.input({"type": "text", "placeholder": "Type", "value": mtype, "on_change": lambda e: set_type(e['target']['value'])}),
                             html.input({"type": "number", "placeholder": "Ports", "value": ports, "on_change": lambda e: set_ports(e['target']['value'])}),
                             html.button({"onClick": add_model, "style": {"marginLeft": "6px"}}, "Add Model")
                             )
                    )
