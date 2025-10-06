from reactpy import component, html, use_state


# ThemeSwitcher Component
@component
def ThemeSwitcher(children):
    return html.div({"className": "theme-wrapper"}, children)
