from django.shortcuts import render

from django.views import View
from django.http import HttpResponse
# Create your views here.

class IndexView(View):
    def get(self, request):
        return HttpResponse("Hello, world. You're at the accounts index.")