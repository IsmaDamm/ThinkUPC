import datetime
from django.db import models
import hashlib
import jwt

class User(models.Model):
    name = models.CharField(max_length = 255)
    backname = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    
    def save(self, *args, **kwargs):
        self.password = self.make_password(self.password)
        super().save(*args, **kwargs)
        
    def make_password(self = None, password = ''):
        return hashlib.sha256(password.encode()).hexdigest()
        

class Subject(models.Model):
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=7)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.name
    
class File(models.Model):
    id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length = 100)
    path = models.CharField(max_length=100)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.id}: {self.subject}"
    