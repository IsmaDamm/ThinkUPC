
from django.urls import path

from api.views import FileView, SubjectView
from api.views import query, removeAll, uploadFile, preProcessFile, updateFile, getSubjectAll, UserView


urlpatterns = [
    
    path('file/', FileView.as_view(), name='file'),
    path('subject/', SubjectView.as_view(), name='subject'),
    path('subject/<int:id>', SubjectView.as_view(), name='subject_id'),
    path('subject/<int:id>/files', getSubjectAll, name='files_subject'),
    path('file/remove/', removeAll, name='removeAll'),
    path('file/<int:id>', FileView.as_view(), name='new_file'),
    path('file/update/<int:idFile>', updateFile, name="update_file"),
    path('query/', query, name='query'),
    path('file/upload/', uploadFile, name='uploadFile'),
    path('file/process/<int:id>', preProcessFile, name='processFile'),
    path('user/', UserView.as_view(), name='user')
    
]
