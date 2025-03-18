from django.urls import path
from .views import home, ModuleListView, moduleDeleteView, moduleUpdateView

urlpatterns = [
    path('', home, name="home-url"),
    #Modules
    path('modules/', ModuleListView.as_view(), name='module_list'),
    path('modules/edit/<str:id>', moduleUpdateView, name="module_edit"),
    path('modules/delete/<str:id>', moduleDeleteView, name="module_delete"),

]
