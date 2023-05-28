from django.contrib.auth import get_user_model, authenticate
from rest_auth.views import LoginView
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import CustomUser, FriendRequest
from .serializers import UserSerializer, FriendRequestSerializer


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


class SendFriendRequestView(generics.CreateAPIView):
    queryset = FriendRequest.objects.all()
    serializer_class = FriendRequestSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(from_user=self.request.user)


class AcceptFriendRequestView(generics.UpdateAPIView):
    queryset = FriendRequest.objects.all()
    serializer_class = FriendRequestSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def perform_update(self, serializer):
        friend_request = self.get_object()
        if friend_request.to_user == self.request.user:
            serializer.save(status=FriendRequest.ACCEPTED)
            self.request.user.friends.add(friend_request.from_user)

        else:
            return Response({"detail": "Not authorized to accept this friend request."},
                            status=status.HTTP_403_FORBIDDEN)


class DeleteFriendView(generics.DestroyAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def perform_destroy(self, instance):
        self.request.user.friends.remove(instance)
