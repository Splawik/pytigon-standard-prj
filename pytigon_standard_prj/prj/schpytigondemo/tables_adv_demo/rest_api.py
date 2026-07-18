"""OAuth2-protected REST API endpoints for the tables_adv_demo module.

Provides a demo endpoint that requires OAuth2 authentication and demonstrates
handling both GET and POST HTTP methods.
"""
from django.urls import path
from rest_framework import serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope

@api_view(['GET','POST'])
@permission_classes([IsAuthenticated | TokenHasReadWriteScope,])
def hello_world(request):
    """Return a greeting message for GET requests or echo submitted data for POST.

    Requires OAuth2 authentication with either session-based or token-based
    read/write scope.
    """
    print(request.user)
    if request.method == 'POST':
        return Response({"message": "Got some data!", "data": request.data})
    return Response({"message": "Hello, world!"})


urlpatterns = [
    path("hello", hello_world, name="hello"),
]
