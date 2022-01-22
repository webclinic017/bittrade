from django.urls import path
from strategy_worker import views

urlpatterns = [
    path('start_worker', views.StartStrategyContainer.as_view()),
    path('stop_worker', views.StopStrategyContainer.as_view()),
    path('is_enabled', views.IsStrategyWorkerEnabled.as_view()),
]
