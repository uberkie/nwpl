"""Signal handlers for planning app.

We implement lightweight post_save/post_delete handlers for DeviceModel that:
- send a Channels group message so any websocket consumer can react
- attempt to call an in-process notifier (if present) so ReactPy components
  subscribed to that notifier reload immediately in a single-process dev server

This file intentionally tolerates absence of Channels or the notifier so it
won't crash in minimal environments.
"""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from django.conf import settings

try:
	# Local import to avoid import-time DB access
	from .models import DeviceModel
except Exception:
	DeviceModel = None

try:
	from channels.layers import get_channel_layer
	from asgiref.sync import async_to_sync
except Exception:
	get_channel_layer = None
	async_to_sync = None


def _notify_inprocess():
	"""Call in-process notifier.notify() if the module exists.

	This call is optional — if the notifier module isn't present (for example
	in some CI or test environments), we simply ignore the error.
	"""
	try:
		# import lazily; reactpy_components may not exist in all environments
		from reactpy_components import _notifier
		try:
			# prefer a function named notify()
			if hasattr(_notifier, "notify"):
				_notifier.notify()
		except Exception:
			# swallow notifier errors — we don't want signal handlers to raise
			pass
	except Exception:
		# notifier not available — no-op
		return


def _send_channel_message(event_type, instance_id):
	"""Send a small message on the channel layer group (if available).

	The websocket consumer in this project listens on group "chat_general" so
	we use that (safe no-op if channels isn't installed).
	"""
	if get_channel_layer is None or async_to_sync is None:
		return
	try:
		layer = get_channel_layer()
		# ChatConsumer.chat_message expects event to carry message_id and content
		payload = {
			"message_id": f"device_model:{instance_id}",
			"content": {"event": event_type, "model": "DeviceModel", "id": instance_id},
		}
		# send to a well-known group; consumers can choose to handle this
		async_to_sync(layer.group_send)("chat_general", {"type": "chat_message", **payload})
	except Exception:
		# Channels not configured or send failed — ignore
		pass


@receiver(post_save)
def device_model_saved(sender, instance, created, **kwargs):
	# only act on DeviceModel saves (avoid acting on unrelated models)
	if DeviceModel is None or sender is not DeviceModel:
		return
	try:
		_notify_inprocess()
		_send_channel_message("created" if created else "updated", getattr(instance, "id", None))
	except Exception:
		# keep signal handlers robust
		pass


@receiver(post_delete)
def device_model_deleted(sender, instance, **kwargs):
	if DeviceModel is None or sender is not DeviceModel:
		return
	try:
		_notify_inprocess()
		_send_channel_message("deleted", getattr(instance, "id", None))
	except Exception:
		pass