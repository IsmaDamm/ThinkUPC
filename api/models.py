from django.db import models

class Subject(models.Model):
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=7)
    
    def __str__(self):
        return self.name
    
class File(models.Model):
    id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length = 100)
    path = models.CharField(max_length=100)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.id}: {self.subject}"