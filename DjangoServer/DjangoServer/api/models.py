from django.db import models


# Create your models here.
class Count(models.Model):
    cnt = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)