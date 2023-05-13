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

from api.storages import PublicFileStorage, PrivateFileStorage

import openai
from openai.embeddings_utils import get_embedding
from api.classes.Openai import Openai
import os
from django.urls import reverse
from api.crud import Subject, User

publicFileStorage = PublicFileStorage()
privateFileStorage = PrivateFileStorage()

subject = Subject()
user = User()

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

def getTokenBareer(request):
    authorization_header = request.headers.get('Authorization')
    
    if authorization_header and 'Bearer ' in authorization_header:
        return authorization_header.split(' ')[1]
    
    return None

def getUserIdTokenBareer(request):
    
    token = getTokenBareer(request)
    
    if token is None: return None
    
    decode = user.decode_token(token)
    
    if decode is None: return None
    
    id, password = decode
    
    return id
    
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

class UserView(View): #Need token bareer
    @method_decorator(csrf_exempt)
    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request): #Get personal user info
        
        id = getUserIdTokenBareer(request)
        
        if id is None: return failedResponse('Forbidden', 'Token error', 403)
        
        if not user.exists(id): return failedResponse('Bad Request', 'User does not exists', 400)
        
        u = user.get(id)
        
        return succesResponse(
            {
                'id': u.id,
                'name': u.name,
                'backname': u.backname,
                'mail': u.email
            }
        )
    
    def put(self, request): #Update personal user info
        
        id = getUserIdTokenBareer(request)
        
        if id is None: return failedResponse('Forbidden', 'Token error', 403)
        
        if not user.exists(id): return failedResponse('Bad Request', 'User does not exists', 400)
        
        try:
            data = json.loads(request.body)
            
            requiredKeys = ['name', 'mail', 'password']
            
            for k in requiredKeys:
                if k not in data.keys() or len(str(data[k].strip())) == 0:
                    return failedResponse('Bad Request', f"The value '{k}' is required", 400)
                        
        except json.JSONDecodeError:       
            return failedResponse('Bad Request', 'Invalid data JSON', 400)
        
        if 'backname' not in data: data['backname'] = ''
        
        u = user.update(id, data['name'], data['backname'], data['mail'], data['password'])
        
        if u is None: return failedResponse('Forbidden', 'This email already exists', 406)
        
        return succesResponse(
            {
                'id': u.id,
                'name': u.name,
                'backname': u.backname,
                'mail': u.email
            }
        )    
    
    def delete(self, request): #Delete user
        
        id = getUserIdTokenBareer(request)
        
        if id is None: return failedResponse('Forbidden', 'Token error', 403)
        
        if not user.exists(id): return failedResponse('Bad Request', 'User does not exists', 400)
        
        user.remove(id)
        
        return succesResponse('', 204)

@method('POST')
def login(request): #Login mail, pass and return new token
    authorization_header = request.headers.get('Authorization')
    
    if authorization_header and 'Bearer ' in authorization_header:
        token = authorization_header.split(' ')[1]
        
        decode = user.decode_token(token)
        
        if decode is not None:
            id, password = decode
            
            return succesResponse({'id': id, 'token': user.make_token(id, password)})
        
        return failedResponse('Forbidden', 'Invalid token', 403)
    
    try:
        data = json.loads(request.body)
        
        requiredKeys = ['mail', 'password']
        
        for k in requiredKeys:
            if k not in data.keys() or len(str(data[k].strip())) == 0:
                return failedResponse('Bad Request', f"The value '{k}' is required", 400)
                    
    except json.JSONDecodeError:       
        return failedResponse('Bad Request', 'Invalid data JSON', 400)
    
    u = user.login(data['mail'], data['password'])
    
    if u is None: return failedResponse('Forbidden', 'Invalid credentials', 403)
    
    return succesResponse({
        'id': u.id,
        'token': user.make_token(u.id, u.password)
    })
    

@method('POST')
def register(request): #Register and return new token
    try:
        data = json.loads(request.body)
        
        requiredKeys = ['name', 'mail', 'password']
        
        for k in requiredKeys:
            if k not in data.keys() or len(str(data[k].strip())) == 0:
                return failedResponse('Bad Request', f"The value '{k}' is required", 400)
                    
    except json.JSONDecodeError:       
        return failedResponse('Bad Request', 'Invalid data JSON', 400)
    
    if 'backname' not in data: data['backname'] = ''
    
    u = user.create(data['name'], data['backname'], data['mail'], data['password'])
    
    if u is None: return failedResponse('Forbidden', "This email already exists")
    
    token = user.make_token(u.id, u.password)
    
    return succesResponse({
        'token': token
    });

class SubjectView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        return super().dispatch(request, *args, **kwargs)
    
    def __init__(self):
        self.subject = subject
    
    def post(self, request):
        
        id = getUserIdTokenBareer(request)
        
        if id is None or not user.exists(id): return failedResponse('Forbidden', 'Token error', 403)
        
        try:
            data = json.loads(request.body)
            
            requiredKeys = ['name', 'color']
            
            for k in requiredKeys:
                if k not in data.keys():
                    return failedResponse('Bad Request', f"The value '{k}' is required", 400)
                        
        except json.JSONDecodeError:       
            return failedResponse('Bad Request', 'Invalid data JSON', 400)
                
        s = self.subject.create(name = data['name'], color = data['color'], userId=id)
        
        return succesResponse(
            {
                'id': s.id,
                'name': s.name,
                'color': s.color
            }
            , 201)

    def get(self, request, id = None):
        
        userId = getUserIdTokenBareer(request)
        
        if userId is None or not user.exists(userId): return failedResponse('Forbidden', 'Token error', 403)
                
        data = self.subject.get(userId, id)
        
        if id is None: return succesResponse(
            [
                {
                    'id': x.id,
                    'name': x.name,
                    'color': x.color
                } 
                for x in data]
            )
        
        if not self.subject.exists(id, userId): return failedResponse('Not Acceptable', f"The id '{id}' does not exist", 406)
        
        return succesResponse(
            {
                'id': data.id,
                'name': data.name,
                'color': data.color
            } 
        )
    
    def delete(self, request, id = None):
        
        userId = getUserIdTokenBareer(request)
        
        if userId is None or not user.exists(userId): return failedResponse('Forbidden', 'Token error', 403)
        
        if id is None:
            self.subject.remove(userId)
            return succesResponse('', 204)    

        if not self.subject.exists(id, userId): return failedResponse('Not Acceptable', f"The id '{id}' does not exist", 406)
        
        r = self.subject.remove(userId, id)
                
        return succesResponse('', 204)
    
    def put(self, request, id = None):
        
        userId = getUserIdTokenBareer(request)
        
        if userId is None or not user.exists(userId): return failedResponse('Forbidden', 'Token error', 403)
        
        if id is None or id <= 0: return failedResponse('Bad Request', f"Invalid Id", 400)
        
        if not self.subject.exists(id, userId): return failedResponse('Not Acceptable', f"The '{id}' dose not exists", 406)
        
        try:
            data = json.loads(request.body)
            
            requiredKeys = ['name', 'color']
            
            for k in requiredKeys:
                if k not in data.keys():
                    return failedResponse('Bad Request', f"The value '{k}' is required", 400)
                        
        except json.JSONDecodeError:       
            return failedResponse('Bad Request', 'Invalid data JSON', 400)
        
        s = self.subject.update(id, data['name'], data['color'], userId)

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
        
        userId = getUserIdTokenBareer(request)
        
        if userId is None or not user.exists(userId): return failedResponse('Forbidden', 'Token error', 403)        
        
        if id is not None and id <= 0: return failedResponse('Bad Request', 'Invalid id', 400)
        
        data = self.process.getDataDocuments(userId, id)
        
        if id is not None:
                        
            if data == False: return failedResponse('Not Acceptable', f"The id '{id}' does not exist", 406)
            
            data['url'] = "/" + settings.PUBLIC_MEDIA_URL + str(data['id']) + ".pdf"
        else:
            for n in data:
                n['url'] = "/" + settings.PUBLIC_MEDIA_URL + str(n['id']) + ".pdf"
        
        return succesResponse(data)
     
    def post(self, request, id = None):
        
        userId = getUserIdTokenBareer(request)
        
        if userId is None or not user.exists(userId): return failedResponse('Forbidden', 'Token error', 403)
                
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
                                
        data = self.process.loadNewFile(file, pdfName, name, urlPublicStorage.localPath, id, userId)
                
        if data == False: return failedResponse('Not Acceptable', f"The subject id '{id}' does not exist", 406)   
                
        data['url'] = urlPublicStorage.publicURL
                
        return succesResponse(data, 201)
    
    def put(self, request, id = None):
        
        userId = getUserIdTokenBareer(request)
        
        if userId is None or not user.exists(userId): return failedResponse('Forbidden', 'Token error', 403)
        
        if id is None or id <= 0: return failedResponse('Bad Request', 'Invalid id', 400)

        try:
            data = json.loads(request.body)
            
            requiredKeys = ['name', 'subject']
            
            for k in requiredKeys:
                if k not in data.keys():
                    return failedResponse('Bad Request', f"The value '{k}' is required", 400)
                        
        except json.JSONDecodeError:       
            return failedResponse('Bad Request', 'Invalid data JSON', 400)

        result = self.process.updateDataDocument(id, data['name'], data['subject'], userId)
    
        if result == False: return failedResponse('Not Acceptable', f"The file id '{id}' or subject id '{data['subject']}' does not exist", 406)
        
        result['url'] = "/" + settings.PUBLIC_MEDIA_URL + str(id) + ".pdf"
        
        return succesResponse(result)
        
    def delete(self, request, id = None):
        
        userId = getUserIdTokenBareer(request)
        
        if userId is None or not user.exists(userId): return failedResponse('Forbidden', 'Token error', 403)
        
        if id is None or id <= 0: return failedResponse('Bad Request', 'Invalid id', 400)
        
        if self.process.deleteDocument(userId, id):
            self.publicFileStorage.remove(str(id) + ".pdf")
            return succesResponse('', 204)
        
        return failedResponse('Not Acceptable', f"The id '{id}' does not exist", 406)                       
    
@method('GET')  
def query(request, id = None ):
    
    userId = getUserIdTokenBareer(request)
        
    if userId is None or not user.exists(userId): return failedResponse('Forbidden', 'Token error', 403)
    
    if id is None or id <= 0: return failedResponse('Bad Request', 'Subject id invalid')
    
    if 'q' not in request.GET: return failedResponse('Bad Request', "Paramettre 'q' is required", 400)
    
    query = request.GET.get('q')
    
    fileId = request.GET.get('file') if 'file' in request.GET else None
    
    useInternet = 'use_internet' in request.GET
    
    result = process.queryDocuments(query, id, userId, fileId, useInternet=useInternet)
    
    if result == False:
        return failedResponse('Not Acceptable', f"The subject id '{id}' does not exists", 406)
        
    if result is None:
        return failedResponse('Internal Server Error', 'Unexpected response from Openai', 500)
        
    for r in result['id_results']:
        r['url'] = "/" + settings.PUBLIC_MEDIA_URL + r['id'] + ".pdf"
    
    result['query'] = query
    
    return succesResponse(result)

@method('POST')
def queryChat(request, id = None):
    userId = getUserIdTokenBareer(request)
        
    if userId is None or not user.exists(userId): return failedResponse('Forbidden', 'Token error', 403)
    
    if id is None or id <= 0: return failedResponse('Bad Request', 'Subject id invalid')
    
    try:
        data = json.loads(request.body)
        
        requiredKeys = ['q', 'chat', 'context']
        
        for k in requiredKeys:
            if k not in data.keys():
                return failedResponse('Bad Request', f"The value '{k}' is required", 400)
                    
    except json.JSONDecodeError:       
        return failedResponse('Bad Request', 'Invalid data JSON', 400)    

    query = str(data['q'])
    context = str(data['context'])
    fileId = data['file'] if 'file' in data.keys() else None
    chat = data['chat']
    useInternet = data['use_internet'] if 'use_internet' in data.keys() else False
    
    result = process.queryDocuments(query, id, userId, fileId, chat=chat, context = context, useInternet=useInternet)
    
    if result == False:
        return failedResponse('Not Acceptable', f"The subject id '{id}' does not exists", 406)
        
    if result is None:
        return failedResponse('Internal Server Error', 'Unexpected response from Openai', 500)
        
    if 'id_results' in result:
        for r in result['id_results']:
            r['url'] = "/" + settings.PUBLIC_MEDIA_URL + r['id'] + ".pdf"
    
    result['query'] = query
    
    return succesResponse(result)    

@method('DELETE')
def removeAll(request):
    userId = getUserIdTokenBareer(request)
    
    if userId is None or not user.exists(userId): return failedResponse('Forbidden', 'Token error', 403)
    
    idsRemove = process.deleteAllDocuments(userId)
    
    for id in idsRemove:
        publicFileStorage.remove(id + ".pdf")
        
    return succesResponse('', 204)

@method('POST')
def updateFile(request, idFile = None):
    
    userId = getUserIdTokenBareer(request)
    
    if userId is None or not user.exists(userId): return failedResponse('Forbidden', 'Token error', 403)
    
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
            
    data = process.updateDataDocument(idFile, name, id, userId)
    
    if data == False: return failedResponse('Not Acceptable', f"The file id '{idFile}' or subject id '{id}' does not exist", 406)
        
    data = process.updatePreProcess(idFile, file, userId)
    
    if data == False: return failedResponse('Not Acceptable', f"The file id '{idFile}' does not exist", 406)
    
    data = process.getDataDocuments(userId, idFile)
    
    data['url'] = "/" + settings.PUBLIC_MEDIA_URL + str(idFile) + ".pdf"
    
    return succesResponse(data) if publicFileStorage.update(file, str(idFile) + '.pdf') else failedResponse('Not Acceptable', f"File '{idFile}' not found", 406)
      
@method('GET')
def getSubjectAll(request, id = None):
    
    userId = getUserIdTokenBareer(request)
    
    if userId is None or not user.exists(userId): return failedResponse('Forbidden', 'Token error', 403)
    
    if id is None or id <= 0: return failedResponse('Bad Request', 'Invalid Id', 400)
    
    if not subject.exists(id, userId): return failedResponse('Not Acceptable', f"The id '{id}' does not found", 406)
    
    files = subject.getFiles(id, userId)
    
    return succesResponse(
        [
            {
                'id': str(f.id),
                'name': f.name,
                'url': "/" + settings.PUBLIC_MEDIA_URL + str(f.id) + ".pdf"    
            } for f in files
        ]
    )
    

