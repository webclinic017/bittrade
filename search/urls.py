from django.urls import path
from . import views

urlpatterns = [
    path('instruments', views.SearchTicker.as_view()),
]
