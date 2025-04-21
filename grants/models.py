from django.db import models

class Grant(models.Model):
    category = models.CharField(max_length=100)
    description = models.TextField()
    link = models.URLField()
    deadline = models.DateField()

    def __str__(self):
        return self.description