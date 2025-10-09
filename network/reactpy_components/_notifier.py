"""Simple in-process notifier for dev-time push updates.

This is intentionally tiny: components can subscribe a callable and will be
called when notify() is invoked. It's not distributed and not persistent —
it's only for the running process (dev server).
"""
import threading

_lock = threading.Lock()
_subscribers = []

def subscribe(fn):
    with _lock:
        _subscribers.append(fn)

    def unsubscribe():
        with _lock:
            try:
                _subscribers.remove(fn)
            except ValueError:
                pass

    return unsubscribe

def notify():
    # snapshot subscribers to avoid holding lock while calling
    with _lock:
        subs = list(_subscribers)
    for s in subs:
        try:
            s()
        except Exception:
            # swallow errors — subscribers should be robust
            pass
