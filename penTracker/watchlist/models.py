from django.db import models
from inventory.models import PenModel

# Create your models here.
class WatchListItem(models.Model):
    pen_model = models.ForeignKey(PenModel, on_delete=models.CASCADE)
    colour = models.CharField(max_length=50, blank=True)
    notes = models.TextField(blank=True)
    date_added = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ['-date_added']

    def __str__(self):
        return f"Watching: {self.pen_model}"
