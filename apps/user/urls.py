from django.urls import path
from .views import userLogin, logout_view
from .views_extras import user, group, permission

urlpatterns = [
    path('login', userLogin, name='login-url'),
    path('logout', logout_view, name='logout-url'),

    #User
    path('users/', user.UserListView.as_view(), name='user_list'),
    path('users/create', user.userCreateView, name="user_create"),
    path('users/edit/<str:id>', user.userUpdateView, name="user_edit"),
    path('users/delete/<str:id>', user.userDeleteView, name="user_delete"),

    #Group
    path('groups/', group.GroupListView.as_view(), name='group_list'),
    path('groups/create', group.groupCreateView, name="group_create"),
    path('groups/edit/<str:id>', group.groupUpdateView, name="group_edit"),
    path('groups/delete/<str:id>', group.groupDeleteView, name="group_delete"),

    #Permission
    path('permissions/', permission.PermissionListView.as_view(), name='permission_list'),
    path('permissions/create', permission.permissionCreateView, name="permission_create"),
    path('permissions/edit/<str:id>', permission.permissionUpdateView, name="permission_edit"),
    path('permissions/delete/<str:id>', permission.permissionDeleteView, name="permission_delete"),
]