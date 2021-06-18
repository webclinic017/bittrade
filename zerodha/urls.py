from django.urls import path
from django.urls import path
from . import views


urlpatterns = [
    path('zerodha_auth', views.zerodha_auth),
    path('zerodha_login/access_token', views.ZerodhaAccessToken.as_view()),
    path('get/zerodha_login_url', views.ZerodhaLoginUrl.as_view()),
    path('place/market_order/buy', views.MarketOrderBuy.as_view()),
    path('place/market_order/sell', views.MarketOrderSell.as_view()),
    path('place/limit_order/buy', views.LimitOrderBuy.as_view()),
    path('place/limit_order/sell', views.LimitOrderSell.as_view())
]