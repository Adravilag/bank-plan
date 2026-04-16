import hashlib
import secrets

from django.contrib.auth import authenticate
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status


@api_view(['POST'])
def login_view(request):
    username = request.data.get('username', '')
    password = request.data.get('password', '')

    if not username or not password:
        return Response(
            {'error': 'Usuario y contraseña son requeridos'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = authenticate(username=username, password=password)

    if user is None:
        return Response(
            {'error': 'Credenciales inválidas'},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    # Generate a simple token (for production, use djangorestframework-simplejwt)
    raw_token = secrets.token_hex(32)
    token = hashlib.sha256(raw_token.encode()).hexdigest()

    return Response({
        'token': token,
        'user': {
            'id': user.id,
            'username': user.username,
        },
    })
