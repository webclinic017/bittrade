from django.http.response import HttpResponse
from django.shortcuts import render
from kiteconnect.connect import KiteConnect
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import APIException
from rest_framework import status
from .serializers import UserProfileSerializer
from .models import UserProfile
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from rest_framework.authtoken.models import Token


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
            raise APIException("profile dosent exist",
                               status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.data, status=status.HTTP_200_OK)


class ZerodhaLoginUrl(APIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request):
        try:
            login_url = request.user.userprofile.kite.login_url()
        except:
            raise APIException("profile dosent exist",
                               status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({
            "login_url": login_url
        })
