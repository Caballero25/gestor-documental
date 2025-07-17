from django.urls import path
from .views import home
from .views_extras import modules, submodules, sequence

urlpatterns = [
    path('', home, name="home-url"),
    #Modules
    path('modules/', modules.ModuleListView.as_view(), name='module_list'),
    path('modules/create', modules.moduleCreateView, name="module_create"),
    path('modules/edit/<str:id>', modules.moduleUpdateView, name="module_edit"),
    path('modules/delete/<str:id>', modules.moduleDeleteView, name="module_delete"),

    #Sub Modules
    path('submodules/', submodules.SubModuleListView.as_view(), name='submodule_list'),
    path('submodules/create', submodules.subModuleCreateView, name="submodule_create"),
    path('submodules/edit/<str:id>', submodules.subModuleUpdateView, name="submodule_edit"),
    path('submodules/delete/<str:id>', submodules.subModuleDeleteView, name="submodule_delete"),

    #Secuenciales
    path('sequence/', sequence.SequenceListView.as_view(), name='sequence_list'),
    path('sequence/create', sequence.sequenceCreateView, name="sequence_create"),
    path('sequence/edit/<str:id>', sequence.sequenceUpdateView, name="sequence_edit"),
    path('sequence/delete/<str:id>', sequence.sequenceDeleteView, name="sequence_delete"),


]
