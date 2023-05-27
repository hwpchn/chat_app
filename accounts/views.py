from django.contrib.auth import get_user_model, authenticate
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_auth.views import LoginView
from .serializers import UserSerializer


class RegisterView(generics.CreateAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.AllowAny,)


class CustomLoginView(LoginView):
    queryset = get_user_model().objects.all()
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')

        user = authenticate(request, email=email, password=password)

        if user is not None:
            return super().post(request, *args, **kwargs)
        else:
            return Response({"detail": "Invalid email/password."}, status=status.HTTP_400_BAD_REQUEST)
