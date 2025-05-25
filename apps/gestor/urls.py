from django.urls import path, re_path
from .views import firstSteptUploadView, secondSteptUploadView, editDocumentView, DocumentListView, documentDeleteView
from .email_service import sendDocumentLink, searchDocuments, sendEmailDocuments, downloadDocument
from .document_detail import DocumentView
from .firma_electronica import signDocument, verificar_firmas
urlpatterns = [
    #CRUD Documents
    path('documents/', DocumentListView.as_view(), name='document_list'),
    re_path(r'^upload/stept/first/(?:(?P<id>\d+)/)?$', firstSteptUploadView, name="first-stept-upload"),
    path('upload/stept/second/<str:id>', secondSteptUploadView, name="second-stept-upload"),
    path('document/edit/<str:id>', editDocumentView, name="edit_document_view"),
    path('document/delete/<str:id>', documentDeleteView, name="document_delete"),
    
    #Email
    path('document/send/email/', sendDocumentLink, name="send_email_link"),
    path('document/search/', searchDocuments, name="document_search"),
    path('send/email/', sendEmailDocuments, name="send_email_documents"),
    path('download/document/<str:token>', downloadDocument, name="download_documents"),
    path('ver/<int:pk>/', DocumentView.as_view(), name='document_viewer'),

    #Firma Electrónica
    
    path('firmar/<int:pk>/', signDocument, name='firmarElectronicamente'),
    path('verificar-firma/<str:token>/', verificar_firmas, name='verificar_firmas'),
]
