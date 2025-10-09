from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import DeviceModel

# Import notifier from reactpy_components package. This notifier is in-process
# and will only work when Django and the ReactPy components run in the same
# process (dev server). It triggers clients to reload their catalogue state.
try:
    from reactpy_components._notifier import notify
except Exception:
    # notifier may not be available in some contexts; don't break app import
    def notify():
        return


@receiver(post_save, sender=DeviceModel)
def device_model_saved(sender, instance, created, **kwargs):
    try:
        notify()
    except Exception:
        pass


@receiver(post_delete, sender=DeviceModel)
def device_model_deleted(sender, instance, **kwargs):
    try:
        notify()
    except Exception:
        pass
