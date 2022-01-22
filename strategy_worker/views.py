from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import APIException
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from django.conf import settings
import docker

# Create your views here.


class StartStrategyContainer(APIView):
    permission_classes = [IsAuthenticated, ]

    def post(self, request):
        client = docker.from_env()
        token = Token.objects.get(user=request.user).key

        scheme = request.is_secure() and 'https' or 'http'
        host = request.get_host()
        uri = f'{scheme}://{host}'

        container = client.containers.run(settings.DOCKER_STRATEGY_IMAGE, detach=True, environment={
            'API_KEY': request.user.userprofile.api_key,
            'ACCESS_TOKEN': request.user.userprofile.access_token,
            'AUTH_TOKEN': token,
            'BITTRADE_HOST': uri
        }, network_mode='host')

        self.request.user.strategyworker.docker_container_id = container.id
        self.request.user.strategyworker.enabled = True
        self.request.user.strategyworker.save()

        return Response({
            "message": "started docker container"
        }, status=status.HTTP_200_OK)


class StopStrategyContainer(APIView):
    permission_classes = [IsAuthenticated, ]

    def post(self, request):
        container = self.request.user.strategyworker.container

        try:
            container.kill()
        except:
            pass

        self.request.user.strategyworker.enabled = False
        self.request.user.strategyworker.save()

        try:
            container.remove()
        except:
            raise APIException("failed to delete the container",
                               code=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({
            "message": "removed the container"
        }, status=status.HTTP_200_OK)


class IsStrategyWorkerEnabled(APIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request):
        return Response({"enabled": request.user.strategyworker.enabled}, status=status.HTTP_200_OK)
