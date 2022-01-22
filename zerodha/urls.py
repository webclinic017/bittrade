from django.urls import path
from . import views


urlpatterns = [
    path('zerodha_auth', views.zerodha_auth),
    path('zerodha_login/access_token', views.ZerodhaAccessToken.as_view()),
    path('pnl/', views.PnlAPI.as_view()),
    path('margins/', views.MarginsAPI.as_view()),
    path('positions/', views.PositionsAPI.as_view()),
    path('execute_trade/', views.ExecuteTrade.as_view()),
]
