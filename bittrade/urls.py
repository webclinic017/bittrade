"""bittrade URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from .views import index, TokenAuthenticationView

urlpatterns = [
    path('zerodha/', include('zerodha.urls')),
    path('users/', include('users.urls')),
    path('strategy_builder/', include('strategy_builder.urls')),
    path('admin/', admin.site.urls),
    path('api-token-auth/', TokenAuthenticationView.as_view()),
    path('strategy_worker/', include('strategy_worker.urls')),
    path('notifier/', include('trade_notifier.urls')),
    path('search/', include('search.urls')),
    path('', index),
]
