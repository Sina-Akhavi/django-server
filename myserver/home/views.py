from django.shortcuts import render

from rest_framework.views import APIView


class HomeView(APIView):
    def get(self, request):
        return render(request, 'home/index.html')
