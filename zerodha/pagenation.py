from rest_framework.pagination import PageNumberPagination

class OrdersPagenation(PageNumberPagination):
    page_size = 20
    page_query_param = 'page'