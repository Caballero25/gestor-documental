from django.urls import path
from .views import home, ModuleListView, moduleDeleteView, moduleUpdateView, moduleCreateView

urlpatterns = [
    path('', home, name="home-url"),
    #Modules
    path('modules/', ModuleListView.as_view(), name='module_list'),
    path('modules/create', moduleCreateView, name="module_create"),
    path('modules/edit/<str:id>', moduleUpdateView, name="module_edit"),
    path('modules/delete/<str:id>', moduleDeleteView, name="module_delete"),

]
