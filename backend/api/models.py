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
    lookahead_lat = models.FloatField()
    lookahead_lng = models.FloatField()

    def __str__(self):
        return f"Stoplight {self.id} in Group {self.group.id} at ({self.lat}, {self.lng})"
        # return f"Stoplight {self.id} in Group {self.group.id} ({self.direction})"