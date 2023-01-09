from django.db import models


class Dataset(models.Model):
    name = models.CharField(max_length=200, unique=True)
    data = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Box(models.Model):
    x0 = models.FloatField()
    y0 = models.FloatField()
    size = models.FloatField()
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
