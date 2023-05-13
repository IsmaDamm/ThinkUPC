
from django.urls import path

from api.views import FileView, SubjectView
from api.views import query, removeAll, updateFile, getSubjectAll, UserView, register, login, queryChat
from api.middleware import AuthView, AuthFun

urlpatterns = [
    
    path('file/', AuthView(FileView()), name='file'),
    path('subject/', AuthView(SubjectView()), name='subject'),
    path('subject/<int:id>', AuthView(SubjectView()), name='subject_id'),
    path('subject/<int:id>/files', AuthFun(getSubjectAll), name='files_subject'),
    path('file/remove/', AuthFun(removeAll), name='removeAll'),
    path('file/<int:id>', AuthView(FileView()), name='new_file'),
    path('file/update/<int:idFile>', AuthFun(updateFile), name="update_file"),
    path('query/<int:id>/', AuthFun(query), name='query'),
    path('chat/query/<int:id>/', AuthFun(queryChat), name='query'),
    path('user/', AuthView(UserView()), name='user'),
    
    path('user/register/', register, name='user_register'),
    path('user/login/', login, name='check_token')    
]
