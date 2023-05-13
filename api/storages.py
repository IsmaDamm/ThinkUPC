
from dataclasses import dataclass
import os
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import abc
import pandas as pd
from pandas._typing import IndexLabel
from typing import Literal


class FileStorage(abc.ABC):
    
    def __init__(self, mediaLocation = None):
        self.mediaLocation = mediaLocation
        
        if mediaLocation is not None:
       
            if not self.existsFolder(settings.BASE_DIR / settings.STORAGE_ROOT):
                os.mkdir(settings.BASE_DIR / settings.STORAGE_ROOT)
                
            if not self.existsFolder(settings.BASE_DIR / mediaLocation):
                os.mkdir(settings.BASE_DIR / mediaLocation)
    
    @abc.abstractmethod
    def read(self, name):
        pass
    
    @abc.abstractmethod
    def save(self, file, name):
        pass
    
    def remove(self, name):
        
        if not self.exists(name): return False
        
        os.remove(settings.BASE_DIR / self.mediaLocation / name)
        
        return True
    
    def update(self, file, name):
        
        if not self.exists(name): return False
        
        self.remove(name)
        self.save(file, name)
        
        return True
        
    
    def removeAllFiles(self, _path = ''):
        
        path = settings.BASE_DIR / self.mediaLocation / _path
        
        for file in os.listdir(path):
            file_path = os.path.join(path, file)
            
            if os.path.isfile(file_path):
                os.remove(file_path)
            else:
                self.removeAllFiles(file_path)
    
    def removeAll(self, _path = ''):
        
        path = settings.BASE_DIR / self.mediaLocation / _path
        
        for file in os.listdir(path):
            file_path = os.path.join(path, file)
            
            os.remove(file_path)
    
    def exists(self, name):
        return os.path.exists(settings.BASE_DIR / self.mediaLocation / name)
    
    def existsFolder(self, name):
        return os.path.exists(settings.BASE_DIR / self.mediaLocation / name) and os.path.isdir(settings.BASE_DIR / self.mediaLocation / name)
    
    def mkdir(self, name):
        os.mkdir(settings.BASE_DIR / self.mediaLocation / name)
    
    def readCsv(self, name, _index_col = None):
        
        if not self.exists(name): return None
        
        return pd.read_csv(settings.BASE_DIR / self.mediaLocation / name) if _index_col is None else pd.read_csv(settings.BASE_DIR / self.mediaLocation / name, index_col=_index_col)
    
    def saveCsv(self, df, name):
        df.to_csv(settings.BASE_DIR / self.mediaLocation / name)
    


@dataclass
class UrlPublicStorage:
    localPath: str
    publicURL: str
class PublicFileStorage(FileStorage):
    
    def __init__(self):
        super().__init__(settings.PUBLIC_MEDIA_LOCATION)
    
    def read(self, name):
        fs = FileSystemStorage(location=settings.MEDIA_ROOT)
    
        path = fs.path(name)
        
        if not os.path.exists(path):
            return None
        with fs.open(name) as f:
            file = f.read()
            
            return file
        
    def save(self, file, name):
        fs = FileSystemStorage(location=settings.MEDIA_ROOT)
        filename = fs.save(name, file)
        return UrlPublicStorage(os.path.join(settings.PUBLIC_MEDIA_LOCATION, name), fs.url(filename))       

    
    
class PrivateFileStorage(FileStorage):
    
    def __init__(self):
        super().__init__(settings.PRIVATE_MEDIA_LOCATION)
    
    def save(self, file, name):    
        fs = FileSystemStorage(location=settings.MEDIA_ROOT)
        fs.save(name, file)
        return os.path.join(settings.PRIVATE_MEDIA_LOCATION, name)
    
    def read(self, name):
        pass