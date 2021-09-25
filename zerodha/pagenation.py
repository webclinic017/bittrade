from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from collections import OrderedDict

class OrdersPagenation(PageNumberPagination):
    page_size = 10
    page_query_param = 'page'
    
    def get_paginated_response(self, data):
        url = self.get_next_link()
        
        url.replace("http", "https")
        url.replace("localhost:8000", "ws.bittrade.space")
        
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('next', url),
            ('previous', self.get_previous_link()),
            ('results', data),
            ('page_number', self.page.number)
        ]))