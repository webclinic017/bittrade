from django.urls import path
from . import views

urlpatterns = [
    path('create_strategy', views.CreateStrategy.as_view(), name='create_strategy'),
    path('get_strategies', views.StrategyList.as_view(), name='strategy_list'),
    path('toggle_strategy/<int:pk>',
         views.ToggleStrategy.as_view(), name='toggle_strategy'),
    path('delete_strategy/<int:pk>',
         views.DeleteStrategy.as_view(), name='delete_strategy'),
]
