from typing import Any

from api.views import failedResponse

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

class AuthMiddleware:
        
    def process_view(self, request, view, *args: Any, **kwds: Any):
        
        check = self.__check(request)

        if check == True: 
            
            if request.method == 'GET': return view.get(request, *args, **kwds)
            if request.method == 'POST': return view.post(request, *args, **kwds)
            if request.method == 'DELETE': return view.delete(request, *args, **kwds)
            if request.method == 'PUT': return view.put(request, *args, **kwds)
            if request.method == 'PATCH': return view.patch(request, *args, **kwds)

    
        return check
    
    def process_fun(self, request, callback, *args: Any, **kwds: Any):
        check = self.__check(request)

        if check == True: return callback(request, *args, **kwds)

        return check

    def __check(self, request):
        token = self.__tokenBareer(request)
        
        if token == False: return failedResponse('Forbidden', 'A token bareer authentication is required', 403)
                    
        if not self.__isValidToken(token): return failedResponse('Unauthorized', 'Invalid token bareer', 401)
        
        return True  

    def __isValidToken(self, token):
        return True
    
    def __tokenBareer(self, request):
        authorization_header = request.headers.get('Authorization')
        
        if authorization_header and 'Bearer ' in authorization_header:
            return authorization_header.split(' ')[1]
        
        return False
        
def AuthView(view):
    
    auth = AuthMiddleware()
    
    @method_decorator(csrf_exempt)
    def wrapper(request, *args, **kwds):
        return auth.process_view(request, view, *args, **kwds)
    
    return wrapper

def AuthFun(callback):
    auth = AuthMiddleware()
    
    @method_decorator(csrf_exempt)
    def wrapper(request, *args, **kwds):
        return auth.process_fun(request, callback, *args, **kwds)
    
    return wrapper