from django.http.response import HttpResponse
from django.shortcuts import render
from kiteconnect.connect import KiteConnect
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserProfileSerializer
from .models import UserProfile
from pymongo import MongoClient


def update_accesstoken(request):
    mongo_clients = MongoClient(
        "mongodb+srv://jag:rtut12#$@cluster0.alwvk.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"
    )
    api_key, api_secret = '', ''

    if request.method == 'GET':
        flag = False
        if request.GET.get("userid", False):
            collection = mongo_clients["client_details"]["clients"]
            document = collection.find_one(
                {'ZERODHA ID': request.GET['userid']})
            api_key, api_secret = document['API Key'], document['API Secret']
            flag = True

        mongo_clients.close()

        return render(request, "update_accesstoken.html", {'api_key': api_key, 'api_secret': api_secret, 'flag': flag, 'userid': request.GET.get("userid", "")})
    elif request.method == 'POST':

        collection = mongo_clients["client_details"]["clients"]

        api_key = request.POST['api_key']
        api_secret = request.POST['api_secret']

        kite = KiteConnect(api_key)
        access_token = kite.generate_session(
            request.POST['request_token'],
            api_secret
        )
        collection.update_one({'ZERODHA ID': request.POST['userid']}, {
                              "$set": {"ACCESS TOKEN": access_token}})
        mongo_clients.close()
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
