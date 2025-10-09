from django.db import models

# Create your models here.
class DeviceModel(models.Model):
	"""Stores device catalogue entries so the ReactPy dashboard can load them dynamically."""
	category = models.CharField(max_length=128, blank=True, default="")
	type = models.CharField(max_length=128)
	model = models.CharField(max_length=256, blank=True, default="")
	ports = models.IntegerField(default=0)
	display = models.CharField(max_length=256, blank=True, default="")
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"{self.category} / {self.display or self.model}"
