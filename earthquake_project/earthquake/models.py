from django.db import models
from django.utils import timezone

class Earthquake(models.Model):
    latitude = models.FloatField()
    latitude_direction = models.CharField(max_length=1, choices=[('N', 'North'), ('S', 'South')])
    longitude = models.FloatField()
    longitude_direction = models.CharField(max_length=1, choices=[('E', 'East'), ('W', 'West')])
    magnitude = models.FloatField()
    depth = models.FloatField()
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.latitude} {self.latitude_direction}, {self.longitude} {self.longitude_direction}"

class Prediction(models.Model):
    earthquake = models.ForeignKey(Earthquake, on_delete=models.CASCADE)
    predicted_magnitude = models.FloatField()
    confidence = models.FloatField()  # Percentage
    probability = models.FloatField()  # Percentage
    accuracy = models.FloatField(default=0.0)  # Percentage, default to 0
    predicted_location = models.CharField(max_length=255)
    prediction_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Prediction for {self.predicted_location}"
