from django.db import models

# Create your models here.

class StoplightGroup(models.Model):
  lat = models.FloatField()
  lng = models.FloatField()

  def __str__(self):
    return f"Stoplight Group {self.id} at ({self.lat}, {self.lng})"
  
class Stoplight(models.Model):
    group = models.ForeignKey(
        StoplightGroup,
        on_delete=models.CASCADE,
        related_name="stoplights"
    )
    local_id = models.IntegerField()
    lat = models.FloatField()
    lng = models.FloatField()
    direction = models.CharField(
        max_length=10,
        choices=[
            ('N', 'North'),
            ('NE', 'Northeast'),
            ('E', 'East'),
            ('SE', 'Southeast'),
            ('S', 'South'),
            ('SW', 'Southwest'),
            ('W', 'West'),
            ('NW', 'Northwest')
        ],
        blank=True  # optional for now ; can neglect => purpose of blank=True
    )

    def __str__(self):
        return f"Stoplight {self.id} in Group {self.group.id}"
        # return f"Stoplight {self.id} in Group {self.group.id} ({self.direction})"