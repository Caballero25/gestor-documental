from django.urls import path
from .views import home, ModuleListView

urlpatterns = [
    path('', home, name="home-url"),
    #Modules
    path('modules/', ModuleListView.as_view(), name='module_list'),
]
