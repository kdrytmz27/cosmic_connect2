# Dosya: users/urls.py
from django.urls import path
from .views import CreateUserView, UserProfileView, UserListView, UserDetailView
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('', UserListView.as_view(), name='user-list'),
    path('<int:pk>/', UserDetailView.as_view(), name='user-detail'),
    path('register/', CreateUserView.as_view(), name='register'),
    path('login/', obtain_auth_token, name='login'),
    path('profile/', UserProfileView.as_view(), name='profile'),
]