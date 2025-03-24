from django.urls import path
from .views import *

urlpatterns = [
    # Metadata Schema
    path('schemas/', MetaDataSchemaListView.as_view(), name='metadataschema_list'),
    path('schemas/create', metaDataSchemaCreateView, name="metadataschema_create"),
    path('schemas/edit/<str:id>', metaDataSchemaUpdateView, name="metadataschema_edit"),
    path('schemas/delete/<str:id>', metaDataSchemaDeleteView, name="metadataschema_delete"),

    # Metadata Schema
    path('fields/', MetaDataFieldListView.as_view(), name='metadatafield_list'),
    path('fields/create', metaDataFieldCreateView, name="metadatafield_create"),
    path('fields/edit/<str:id>', metaDataFieldUpdateView, name="metadatafield_edit"),
    path('fields/delete/<str:id>', metaDataFieldDeleteView, name="metadatafield_delete"),

]
