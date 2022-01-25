from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from entities.search import RedisInstrumentSearch
from rest_framework import status

# Create your views here.


class SearchTicker(APIView):
    def get(self, request: Request):
        search = RedisInstrumentSearch()

        search_param = request.query_params.get('search', '')
        if search_param == '':
            return Response([], status=status.HTTP_200_OK)

        suggestions = search.get_suggestions(search_param)

        return Response(list(suggestions), status=status.HTTP_200_OK)
