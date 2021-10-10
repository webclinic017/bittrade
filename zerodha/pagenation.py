from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from collections import OrderedDict


class OrdersPagenation(PageNumberPagination):
    page_size = 10
    page_query_param = 'page'

    def get_paginated_response(self, data):
        url_next = self.get_next_link()
        url_prev = self.get_previous_link()

        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('next', url_next),
            ('previous', url_prev),
            ('results', data),
            ('page_number', self.page.number)
        ]))
