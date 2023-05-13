import datetime
import json
from pathlib import Path
import random
from typing import Any
from django.conf import settings
from django.http import FileResponse, HttpRequest, HttpResponse, HttpResponseNotFound, JsonResponse
from django.views import View

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from api.classes.ProcessFile import ProcessFile

from api.storages import PublicFileStorage, PrivateFileStorage, DocumentDbStorage

import openai
from openai.embeddings_utils import get_embedding
from api.classes.Openai import Openai
import os
from django.urls import reverse
from api.crud import Subject

publicFileStorage = PublicFileStorage()
privateFileStorage = PrivateFileStorage()
documentDb = DocumentDbStorage()

subject = Subject()

process = ProcessFile(privateFileStorage)

def method(method = 'GET'):
    
    def dec(fun):
        @method_decorator(csrf_exempt)
        def wrapper(request, *args, **kwargs):
            
            if request.method == method.upper(): return fun(request, *args, **kwargs)
            else: return failedResponse('Method Not Allowed', f"The {request.method} is not allowed. You should try the {method.upper()} method", 405)
            
        return wrapper
    
    return dec

def succesResponse(body, _status = 200):
    return HttpResponse(
            json.dumps(
                {
                    'message': 'Success',
                    'result': body
                }
            ), 
            content_type='application/json', 
            status=_status)
    
def failedResponse(errReason, errMessage, _status = 400):
    return HttpResponse(
        json.dumps(
            {
                'message': 'Failed',
                'error': {
                    'reason': errReason,
                    'message': errMessage
                }
            }
        ), 
        content_type='application/json', 
        status=_status)
    
def notImplementedEndPoint(msg = ''):
    return failedResponse('Not implemented', 'This EndPoint is not implemented yet. ' + msg, 501)

def generateId():
    return str(random.randint(1, 100)) + str(int(datetime.datetime.now().strftime("%d%H%M%S%f")))

class PublicFileView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request, path):
        file_path = Path(settings.PUBLIC_MEDIA_LOCATION) / path
        if file_path.is_file():
            return FileResponse(open(file_path, 'rb'), content_type='application/pdf')
        else:
            return HttpResponseNotFound()

class UserView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        return super().dispatch(request, *args, **kwargs)
    
    
    def post(self, request):
        
        authorization_header = request.headers.get('Authorization')

        if authorization_header and 'Bearer ' in authorization_header:
            token = authorization_header.split(' ')[1]
            
            return succesResponse(token)
        
        return notImplementedEndPoint()    

class SubjectView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        return super().dispatch(request, *args, **kwargs)
    
    def __init__(self):
        self.subject = subject
    
    def post(self, request):
        
        try:
            data = json.loads(request.body)
            
            requiredKeys = ['name', 'color']
            
            for k in requiredKeys:
                if k not in data.keys():
                    return failedResponse('Bad Request', f"The value '{k}' is required", 400)
                        
        except json.JSONDecodeError:       
            return failedResponse('Bad Request', 'Invalid data JSON', 400)
                
        s = self.subject.create(name = data['name'], color = data['color'])
        
        return succesResponse(
            {
                'id': s.id,
                'name': s.name,
                'color': s.color
            }
            , 201)

    def get(self, request, id = None):
        
        data = self.subject.get(id)
        
        if id is None: return succesResponse(
            [
                {
                    'id': x.id,
                    'name': x.name,
                    'color': x.color
                } 
                for x in data]
            )
        
        if not self.subject.exists(id): return failedResponse('Not Acceptable', f"The id '{id}' does not exist", 406)
        
        return succesResponse(
            {
                'id': data.id,
                'name': data.name,
                'color': data.color
            } 
        )
    
    def delete(self, request, id = None):
        
        if id is None:
            self.subject.remove()
            return succesResponse('', 204)    

        if not self.subject.exists(id): return failedResponse('Not Acceptable', f"The id '{id}' does not exist", 406)
        
        self.subject.remove(id)
        
        return succesResponse('', 204)
    
    def put(self, request, id = None):
        
        if id is None or id <= 0: return failedResponse('Bad Request', f"Invalid Id", 400)
        
        if not self.subject.exists(id): return failedResponse('Not Acceptable', f"The '{id}' dose not exists", 406)
        
        try:
            data = json.loads(request.body)
            
            requiredKeys = ['name', 'color']
            
            for k in requiredKeys:
                if k not in data.keys():
                    return failedResponse('Bad Request', f"The value '{k}' is required", 400)
                        
        except json.JSONDecodeError:       
            return failedResponse('Bad Request', 'Invalid data JSON', 400)
        
        s = self.subject.update(id, data['name'], data['color'])

        return succesResponse(
            {
                'id': s.id,
                'name': s.name,
                'color': s.color
            }
        )


class FileView(View):
    
    def __init__(self):
        
        global process
        global publicFileStorage
        
        self.process = process
        self.publicFileStorage = publicFileStorage
    
    @method_decorator(csrf_exempt)
    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request, id = None):
        
        if id is not None and id <= 0: return failedResponse('Bad Request', 'Invalid id', 400)
        
        data = self.process.getDataDocuments(id)
        
        if id is not None:
                        
            if data == False: return failedResponse('Not Acceptable', f"The id '{id}' does not exist", 406)
            
            data['url'] = "/" + settings.PUBLIC_MEDIA_URL + str(data['id']) + ".pdf"
        else:
            for n in data:
                n['url'] = "/" + settings.PUBLIC_MEDIA_URL + str(n['id']) + ".pdf"
        
        return succesResponse(data)
     
    def post(self, request, id = None):
                
        if 'pdf_file' not in request.FILES:
            return failedResponse('Bad Request', "Pdf file not found by key 'pdf_file'", 400)  
                
        file = request.FILES['pdf_file']

        if file.content_type != 'application/pdf':
            return failedResponse('Unsupported Media Type', 'The file must be PDF file', 415)

        if 'name' not in request.POST:
            return failedResponse('Bad Request', 'The name is required', 400)

        name = str(request.POST.get('name')).strip()
        
        if len(name) == 0:
            return failedResponse('Bad Request', 'The name can not be empty', 400)

        if id is None:
            return failedResponse('Bad Request', 'Invalid subject id', 400)
  
        pdfName = generateId()
                
        urlPublicStorage = self.publicFileStorage.save(file, pdfName + ".pdf")
                                
        data = self.process.loadNewFile(file, pdfName, name, urlPublicStorage.localPath, id)
                
        if data == False: return failedResponse('Not Acceptable', f"The subject id '{id}' does not exist", 406)   
                
        data['url'] = urlPublicStorage.publicURL
                
        return succesResponse(data, 201)
    
    def put(self, request, id = None):
        if id is None or id <= 0: return failedResponse('Bad Request', 'Invalid id', 400)

        try:
            data = json.loads(request.body)
            
            requiredKeys = ['name', 'subject']
            
            for k in requiredKeys:
                if k not in data.keys():
                    return failedResponse('Bad Request', f"The value '{k}' is required", 400)
                        
        except json.JSONDecodeError:       
            return failedResponse('Bad Request', 'Invalid data JSON', 400)

        result = self.process.updateDataDocument(id, data['name'], data['subject'])
    
        if result == False: return failedResponse('Not Acceptable', f"The file id '{id}' or subject id '{data['subject']}' does not exist", 406)
        
        result['url'] = "/" + settings.PUBLIC_MEDIA_URL + str(id) + ".pdf"
        
        return succesResponse(result)
        
    def delete(self, request, id = None):
        
        if id is None or id <= 0: return failedResponse('Bad Request', 'Invalid id', 400)
        
        if self.process.deleteDocument(id):
            self.publicFileStorage.remove(str(id) + ".pdf")
            return succesResponse('', 204)
        
        return failedResponse('Not Acceptable', f"The id '{id}' does not exist", 406)                       
    
@method('GET')  
def query(request):
    
    query = request.GET.get('q')
    
    result = process.queryDocuments(query)
        
    if result is None:
        return failedResponse('Internal Server Error', 'Unexpected response from Openai', 500)
        
    for r in result['id_results']:
        r['url'] = "/" + settings.PUBLIC_MEDIA_URL + r['id'] + ".pdf"
    
    result['query'] = query
    
    return succesResponse(result)

@method('DELETE')
def removeAll(request):
    process.deleteAllDocuments()
    
    publicFileStorage.removeAllFiles()
    
    return succesResponse('', 204)

@method('POST')
def updateFile(request, idFile = None):
    
    if idFile is None or idFile <= 0: return failedResponse('Bad Request', 'Invalid id', 400)

    if 'pdf_file' not in request.FILES:
        return failedResponse('Bad Request', "Pdf file not found by key 'pdf_file'", 400)  
            
    file = request.FILES['pdf_file']

    if file.content_type != 'application/pdf':
        return failedResponse('Unsupported Media Type', 'The file must be PDF file', 415)

    columns = ['name', 'subject']
    
    for c in columns:
        if c not in request.POST:
            return failedResponse('Bad Request', f"The {c} is required", 400)      
    
    name = str(request.POST.get('name')).strip()
    
    if len(name) == 0: return failedResponse('Bad Request', 'The name can not be empty', 400)
    
    id = int(request.POST.get('subject'))
            
    data = process.updateDataDocument(idFile, name, id)
    
    data['url'] = "/" + settings.PUBLIC_MEDIA_URL + str(idFile) + ".pdf"
    
    data = process.updatePreProcess(idFile, file)
    
    if data == False: return failedResponse('Not Acceptable', f"The file id '{idFile}' does not exist", 406)
    
    data = process.getDataDocuments(idFile)
    
    return succesResponse(data) if publicFileStorage.update(file, str(idFile) + '.pdf') else failedResponse('Not Acceptable', f"File '{idFile}' not found", 406)
      

@method('POST')
def uploadFile(request):
    
    if 'pdf_file' not in request.FILES:
        return failedResponse('Bad Request', "Pdf file not found by key 'pdf_file'", 400)  
                
    file = request.FILES['pdf_file']

    if file.content_type != 'application/pdf':
        return failedResponse('Unsupported Media Type', 'The file must be PDF file', 415)
    
    pdfName = generateId()
    
    urlPublicStorage = publicFileStorage.save(file, pdfName + ".pdf")
    
    # documentDb.save(file, pdfName + ".pdf")
    
    dataSave = {}
    
    for key in process.getColumns():
        dataSave[key] = "Unknown"
    
    info_df = process.addCvInfo(pdfName, urlPublicStorage.localPath, dataSave)
    
    process.saveCsvData(info_df)
    
    return succesResponse(
        {
            'id': pdfName,
            'url': urlPublicStorage.publicURL,
        }, 201)

def preProcessFile(request, id = None):
    
    if id is None or id <= 0: return failedResponse('Bad Request', 'Invalid id', 400)
    
    file = publicFileStorage.read(str(id) + ".pdf")
    
    if file is None: return failedResponse('Not Acceptable', f"The id '{id}' does not exist", 406)
    
    chunks_df = process.preProcess(file)
        
    process.saveCsvFile(chunks_df, id)
    
    return succesResponse('', 204)

@method('GET')
def getSubjectAll(request, id = None):
    
    if id is None or id <= 0: return failedResponse('Bad Request', 'Invalid Id', 400)
    
    if not subject.exists(id): return failedResponse('Not Acceptable', f"The id '{id}' does not found", 406)
    
    files = subject.getFiles(id)
    
    return succesResponse(
        [
            {
                'id': str(f.id),
                'name': f.name,
                'url': "/" + settings.PUBLIC_MEDIA_URL + str(f.id) + ".pdf"    
            } for f in files
        ]
    )
    
