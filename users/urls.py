from django.urls import path
from . import views

urlpatterns = [
    path('is_login', views.IsLoggedIn.as_view()),
    path('update/profile', views.UpdateProfile.as_view()),
    path('profile/detail', views.ProfileDetail.as_view()),
    path('update/token', views.update_accesstoken),
    path('zerodha_login_url', views.ZerodhaLoginUrl.as_view())
]
