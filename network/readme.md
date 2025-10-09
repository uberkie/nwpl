in reactpy/svg.py find these two lines:

```
text = make_vdom_constructor("text", allow_children=False)
title = make_vdom_constructor("title", allow_children=False)
```
and change it to:
```
text = make_vdom_constructor("text", allow_children=True)
title = make_vdom_constructor("title", allow_children=True)
```