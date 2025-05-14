from django.contrib import admin
from .models import Earthquake, Prediction

admin.site.register(Earthquake)
admin.site.register(Prediction)