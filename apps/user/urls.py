from django.urls import path
from .views import userLogin, logout_view
from .views_extras import user

urlpatterns = [
    path('login', userLogin, name='login-url'),
    path('logout', logout_view, name='logout-url'),

    #User
    path('users/', user.UserListView.as_view(), name='user_list'),
    path('users/create', user.userCreateView, name="user_create"),
    path('users/edit/<str:id>', user.userUpdateView, name="user_edit"),
    path('users/delete/<str:id>', user.userDeleteView, name="user_delete"),
]