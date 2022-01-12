from django.http.response import HttpResponse
from django.shortcuts import render
from kiteconnect.connect import KiteConnect
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserProfileSerializer
from .models import UserProfile
from zerodha.models import APICredentials


def update_accesstoken(request):
    api_key, api_secret = '', ''

    if request.method == 'GET':
        flag = False
        if request.GET.get("userid", False):
            userid = request.GET.get("userid")
            api = APICredentials.objects.get(userid=userid)
            api_key, api_secret = api.api_key, api.api_secret
            flag = True

        return render(request, "update_accesstoken.html", {'api_key': api_key, 'api_secret': api_secret, 'flag': flag, 'userid': request.GET.get("userid", "")})
    elif request.method == 'POST':
        api_key = request.POST['api_key']
        api_secret = request.POST['api_secret']

        kite = KiteConnect(api_key)
        access_token = kite.generate_session(
            request.POST['request_token'],
            api_secret
        )['access_token']

        api = userid = request.POST.get("userid")
        api = APICredentials.objects.get(userid=userid)
        api.access_token = access_token
        api.save()

        return HttpResponse('updated the token')


class IsLoggedIn(APIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request):
        return Response(status=status.HTTP_200_OK)


class UpdateProfile(APIView):
    permission_classes = [IsAuthenticated, ]

    def put(self, request):
        UserProfile.objects.update_or_create(
            user=request.user,
            defaults=request.data
        )

        return Response(status=status.HTTP_200_OK)


class ProfileDetail(APIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request):
        try:
            serializer = UserProfileSerializer(request.user.userprofile)
        except:
            return Response({
                'message': 'please update your profile'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(serializer.data, status=status.HTTP_200_OK)


class ZerodhaLoginUrl(APIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request):
        login_url = request.user.userprofile.kite.login_url()
        return Response({
            "login_url": login_url
        })
