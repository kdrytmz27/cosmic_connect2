# Dosya: connections/urls.py
from django.urls import path
from .views import LikeUserView, MatchListView, CompatibilityView

urlpatterns = [
    path('like/<int:pk>/', LikeUserView.as_view(), name='like-user'),
    path('matches/', MatchListView.as_view(), name='match-list'),
    path('compatibility/<int:pk>/', CompatibilityView.as_view(), name='compatibility'),
]