from django.urls import path
from trade_notifier import views

urlpatterns = [
    path('trade', views.PublishTrade.as_view()),
]
