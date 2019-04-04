from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

app_name = 'info'

urlpatterns = [
    path('history', views.history, name="history"),
    path('stats', views.stats, name="stats")
]