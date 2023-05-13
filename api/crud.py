from typing import Any
from api.models import Subject as SubjectModel
from api.models import File as FileModel

from django.db import models

import abc

class crud(abc.ABC):
    
    @abc.abstractmethod
    def get(self, id = None):
        pass
    
    @abc.abstractmethod
    def exists(self, id):
        pass
    
    def remove(self, id = None):
        self.get(id).delete()

class Subject(crud):
    
    def create(self, name, color):
        
        s = SubjectModel(name = name, color = color)
        
        s.save()
        
        return s
    
    def update(self, id, name, color):
        
        s = self.get(id)
        
        s.name = name
        s.color = color
        
        s.save()
        
        return s
    
    def get(self, id = None):
        if id is not None: return SubjectModel.objects.get(id=id)
        
        return SubjectModel.objects.all()
    
    def getFiles(self, id):
        
        return SubjectModel.objects.get(id=id).file_set.all()
        
    
    def exists(self, id):
        return SubjectModel.objects.filter(id=id).exists()
    
    
class File(crud):
    
    def __init__(self):
        self.subject = Subject()
    
    def create(self, id, name, path, subjectId = None, subjectObject = None):
        
        if subjectId is not None: subjectObject = self.subject.get(subjectId)
        
        f = FileModel(id = int(id), name = name, path = path, subject = subjectObject)
        
        f.save()
        
        return f
    
    def update(self, id, name, subjectId = None, subjectObject = None):
        p = self.get(id)
        
        p.name = name
        p.subject = subjectObject if subjectId is None else self.subject.get(subjectId)
        
        p.save()
        
        return p
    
    def get(self, id = None):
        if id is not None: return FileModel.objects.get(id=id)
        
        return FileModel.objects.all()
    
    def exists(self, id):
        return FileModel.objects.filter(id=id).exists()