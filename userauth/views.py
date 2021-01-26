import requests
from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from datetime import datetime
from rest_framework.decorators import api_view,permission_classes


# Create your views here.

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def restricted(request, *args, **kwargs):
    date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    message = 'Clock in server current time is'
    return Response(data=message + date, status=status.HTTP_200_OK)


class ActivateUser(GenericAPIView):

    def get(self, request, uid, token, format = None):
        print('Hello')
        payload = {'uid': uid, 'token': token}

        url = "http://localhost:8000/api/v1/auth/users/activation/"
        response = requests.post(url, data = payload)

        if response.status_code == 204:
            return Response({}, response.status_code)
        else:
            return Response(response.json())

