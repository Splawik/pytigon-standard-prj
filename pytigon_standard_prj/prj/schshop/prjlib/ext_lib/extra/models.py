from django.db import models

class Accept(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    key = models.CharField(max_length=256, null=True, blank=True)
    value = models.CharField(max_length=256, null=True, blank=True)
