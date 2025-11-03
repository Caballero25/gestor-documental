from django.urls import path, re_path
from .views import firstSteptUploadView, secondSteptUploadView, editDocumentView, editDocumentIndexacionView, DocumentListView, documentDeleteView, lista_tomos
from .email_service import sendDocumentLink, searchDocuments, sendEmailDocuments, downloadDocument
from .document_detail import DocumentView
from .firma_electronica import signDocument
from .uploadDocumentImage import capture_document_view, get_metadata_fields
from .seq_value import getSeqValue, setSeqValue
from .texto_parametrizable import texto_parametrizable_list, texto_parametrizable_create, texto_parametrizable_update, texto_parametrizable_delete, texto_parametrizable_detail
urlpatterns = [
    #CRUD Documents
    path('documents/', DocumentListView.as_view(), name='document_list'),
    re_path(r'^upload/stept/first/(?:(?P<id>\d+)/)?$', firstSteptUploadView, name="first-stept-upload"),
    path('upload/stept/second/<str:id>', secondSteptUploadView, name="second-stept-upload"),
    path('document/edit/<str:id>', editDocumentView, name="edit_document_view"),
    path('document/edit/<str:id>/<str:anio>', editDocumentView, name="edit_document_view_year"),
    path('document/indexacion/edit/<str:id>', editDocumentIndexacionView, name="edit_document_indexacion_view"),
    path('document/delete/<str:id>', documentDeleteView, name="document_delete"),
    
    #Email
    path('document/send/email/', sendDocumentLink, name="send_email_link"),
    path('document/search/', searchDocuments, name="document_search"),
    path('send/email/', sendEmailDocuments, name="send_email_documents"),
    path('download/document/<str:token>', downloadDocument, name="download_documents"),
    path('ver/<int:pk>/', DocumentView.as_view(), name='document_viewer'),

    #Firma Electrónica
    path('firmar/<int:pk>/', signDocument, name='firmarElectronicamente'),

    #upload with image
    path('capture/', capture_document_view, name='capture_document'),
    path('get_metadata_fields/', get_metadata_fields, name='get_metadata_fields'),

    #seq_value
    path('api/getSeqValue/', getSeqValue, name='get_seq_value'),
    path('api/setSeqValue/', setSeqValue, name='set_seq_value'),

    #Meta datos
    path('listaTomos/', lista_tomos, name='lista_tomo'),

    #Texto parametrizable
    path('textos-parametrizables/', texto_parametrizable_list, name='texto_list'),
    path('textos-parametrizables/create/', texto_parametrizable_create, name='texto_parametrizable_create'),
    path('textos-parametrizables/update/<int:pk>/', texto_parametrizable_update, name='texto_parametrizable_update'),
    path('textos-parametrizables/delete/<int:pk>/', texto_parametrizable_delete, name='texto_parametrizable_delete'),
    path('textos-parametrizables/detail/<int:pk>/', texto_parametrizable_detail, name='texto_parametrizable_detail'),
]

