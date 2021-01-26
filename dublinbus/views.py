from django.shortcuts import redirect
from rest_framework.views import APIView
from rest_framework.response import Response
import requests

# Activate user
class UserActivationView(APIView):
    def get(self, request, uid, token, format=None):
        # Get uid and token from link
        payload = {'uid': uid, 'token': token}
        # Post url
        url = "http://localhost:8000/auth/users/activation/"
        response = requests.post(url, data=payload)
        if response.status_code == 204:
            url = 'http://localhost:4200'
            return redirect(url)
        else:
           return Response(response.json())

# Reset Password
class UserResetPasswordView(APIView):
    def get(self, request, uid, token, format=None):
        url = 'http://localhost:4200/update-pwd/'+uid+'/'+token
        return redirect(url)
