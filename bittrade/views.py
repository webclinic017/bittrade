from django.contrib.auth.models import update_last_login
from django.contrib.auth import get_user_model
from rest_framework.authtoken.views import ObtainAuthToken
from django.http import HttpResponse


def index(request):
    return HttpResponse('thanks for visiting')


class TokenAuthenticationView(ObtainAuthToken):
    """Implementation of ObtainAuthToken with last_login update"""

    def post(self, request):
        result = super(TokenAuthenticationView, self).post(request)
        currentUserModel = get_user_model()
        try:
            user = currentUserModel.objects.get(
                username=request.data['username'])
            update_last_login(None, user)
        except Exception as exc:
            return None
        return result
