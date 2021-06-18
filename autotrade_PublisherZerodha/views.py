from django.http import HttpResponse


def index(request):
    return HttpResponse('thanks for visiting')
