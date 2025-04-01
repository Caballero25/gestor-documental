from django.urls import path, re_path
from .views import firstSteptUploadView, secondSteptUploadView, editDocumentView, DocumentListView, documentDeleteView
from .email_service import sendDocumentLink, search_documents
urlpatterns = [
    #CRUD Documents
    path('documents/', DocumentListView.as_view(), name='document_list'),
    re_path(r'^upload/stept/first/(?P<id>\d+)?/$', firstSteptUploadView, name="first-stept-upload"),
    path('upload/stept/second/<str:id>', secondSteptUploadView, name="second-stept-upload"),
    path('document/edit/<str:id>', editDocumentView, name="edit_document_view"),
    path('document/delete/<str:id>', documentDeleteView, name="document_delete"),
    
    #Email
    path('document/send/email/<str:id>', sendDocumentLink, name="send_email_link"),
    path('document/search/', search_documents, name="document_search"),
]
