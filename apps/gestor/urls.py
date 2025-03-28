from django.urls import path, re_path
from .views import firstSteptUploadView, secondSteptUploadView, editDocumentView

urlpatterns = [
    path('upload/stept/first/', firstSteptUploadView, name="first-stept-upload"),
    path('upload/stept/second/<str:id>', secondSteptUploadView, name="second-stept-upload"),
    path('document/edit/<str:id>', editDocumentView, name="edit_document_view"),
    #Modules
    #path('modules/', modules.ModuleListView.as_view(), name='module_list'),
    #path('modules/create', modules.moduleCreateView, name="module_create"),
    #path('modules/edit/<str:id>', modules.moduleUpdateView, name="module_edit"),
    #path('modules/delete/<str:id>', modules.moduleDeleteView, name="module_delete"),
]
