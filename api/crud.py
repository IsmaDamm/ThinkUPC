import datetime
from typing import Any

import jwt
from api.models import Subject as SubjectModel
from api.models import File as FileModel
from api.models import User as UserModel

from django.db import models

import abc

class crud(abc.ABC):
    
    @abc.abstractmethod
    def get(self, id = None):
        pass
    
    @abc.abstractmethod
    def exists(self, id):
        pass
    
    @abc.abstractmethod
    def remove(self, id = None):
        pass

class User(crud):
    
    def __init__(self):
        self.secret = '99031602'
    
    def get(self, id = None):
                
        if id is not None: return UserModel.objects.get(id=id)
        
        return UserModel.objects.all()
        
    def exists(self, id):
        return UserModel.objects.filter(id=id).exists()

    def create(self, name, backname, email, password):
        
        if UserModel.objects.filter(email=email).exists(): return None
        
        u = UserModel(name = name, backname = backname, email = email, password = password)
        
        u.save()
        
        return u
    
    def update(self, id, name, backname, email, password):
        
        u = UserModel.objects.filter(email=email)
        
        if u.exists() and u[0].id != id: return None
        
        u = self.get(id)
        
        u.name = name
        u.backname = backname
        u.email = email
        u.password = password
        
        u.save()
        
        return u
    
    def remove(self, id = None):
        self.get(id).delete()
    
    def login(self, mail, password):
        try:
            user = UserModel.objects.get(email=mail)
            if user.password == UserModel.make_password(password = password):
                return user
            else:
                return None
        except:
            return None
    
    def make_token(self, user_id, password_hash):
        
        payload = {'id': user_id, 'pass': password_hash, 'exp': datetime.datetime.utcnow() + datetime.timedelta(weeks=1)}
        jwt_token = jwt.encode(payload, self.secret, algorithm='HS256')
        return jwt_token
    
    def decode_token(self, token):
        try:
            decoded_payload = jwt.decode(token, self.secret, algorithms=['HS256'])
            user_id = decoded_payload['id']
            password = decoded_payload['pass']
            expiration = decoded_payload.get('exp')
            if expiration and datetime.datetime.utcnow() > datetime.datetime.fromtimestamp(expiration):
                return None
            return (user_id, password)
        except jwt.InvalidTokenError:
            return None
class Subject(crud):
    
    def __init__(self):
        self.user = User()
    
    def create(self, name, color, userId = None, userObject = None):
        
        if userId is not None: userObject = self.user.get(userId)
        
        s = SubjectModel(name = name, color = color, user = userObject)
        
        s.save()
        
        return s
    
    def update(self, id, name, color, userId):
        
        if not self.exists(id, userId): return None
        
        s = self.get(userId, id)
        
        s.name = name
        s.color = color
        
        s.save()
        
        return s
    
    def get(self, userId, id = None):
        
        if id is not None: 
            return SubjectModel.objects.get(id=id) if self.exists(id, userId) else None
          
        return SubjectModel.objects.filter(user_id = userId)
    
    def getFiles(self, id, userId):
        
        if not self.exists(id, userId): return None
        
        return SubjectModel.objects.get(id=id).file_set.all()
        
    
    def exists(self, id, user_id):
        s = SubjectModel.objects.filter(id=id)
        
        return s.exists() and s[0].user.id == user_id
    
    def remove(self, userId, id = None):        
        self.get(userId, id).delete()
            
class File(crud):
    
    def __init__(self):
        self.subject = Subject()
    
    def create(self, id, name, path, userId, subjectId = None, subjectObject = None):
                
        if subjectId is not None: subjectObject = self.subject.get(userId, subjectId)
        
        if not subjectObject.user.id == userId: return None
        
        f = FileModel(id = int(id), name = name, path = path, subject = subjectObject)
        
        f.save()
        
        return f
    
    def update(self, id, name, userId, subjectId = None, subjectObject = None):
        
        if not self.exists(id, userId): return None
        
        p = self.get(userId, id)
        
        p.name = name
        p.subject = subjectObject if subjectId is None else self.subject.get(userId, subjectId)
        
        p.save()
        
        return p
    
    def get(self, userId, id = None):
        if id is not None: 
            return FileModel.objects.get(id=id) if self.exists(id, userId) else None
        
        return FileModel.objects.filter(subject__user_id=userId)
    
    def exists(self, id, userId):
        f = FileModel.objects.filter(id=id)
        
        return f.exists() and f[0].subject.user.id == userId
    
    def remove(self, userId, id = None):
        self.get(userId, id).delete()