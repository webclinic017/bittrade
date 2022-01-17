from django.urls import path
from . import views

urlpatterns = [
    path('create_strategy', views.CreateStrategy.as_view(), name='create_strategy'),
]
