from django.urls import path
from . import views

urlpatterns = [
    path('stats/', views.stats, name="stats"),
    path('history/', views.req_history, name="history"),
]