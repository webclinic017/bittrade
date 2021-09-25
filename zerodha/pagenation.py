from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from collections import OrderedDict

class OrdersPagenation(PageNumberPagination):
    page_size = 10
    page_query_param = 'page'
    
    def get_paginated_response(self, data):
        url_next = self.get_next_link()
        
        try:
            url_next = url_next.replace("http", "https")
            url_next = url_next.replace("localhost:8000", "ws.bittrade.space")
        except:
            pass
        
        url_prev = self.get_previous_link()
        
        try:
            url_prev = url_prev.replace("http", "https")
            url_prev = url_prev.replace("localhost:8000", "ws.bittrade.space")
        except:
            pass
        
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('next', url_next),
            ('previous', url_prev),
            ('results', data),
            ('page_number', self.page.number)
        ]))