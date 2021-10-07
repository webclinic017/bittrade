from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .serializers import UserProfileSerializer
from .models import UserProfile


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
