from django.contrib.auth import authenticate, get_user_model
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view, permission_classes
from django.db.models import Q
from .serializers import UserSerializer, SignupSerializer
from .models import FriendRequest  # Ensure this import is correct
import time

User = get_user_model()

class SignupView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = SignupSerializer
    permission_classes = [AllowAny]

class LoginView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = SignupSerializer

    def post(self, request, *args, **kwargs):
        email = request.data.get('email').lower()
        password = request.data.get('password')
        user = authenticate(email=email, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
        else:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)

class UserSearchView(generics.ListAPIView):
    serializer_class = UserSerializer

    def get_queryset(self):
        query = self.request.query_params.get('q', '')
        return User.objects.filter(Q(email__iexact=query) | Q(username__icontains=query))

class FriendRequestView(generics.GenericAPIView):
    def post(self, request, *args, **kwargs):
        receiver_email = request.data.get('email').lower()
        try:
            receiver = User.objects.get(email=receiver_email)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        if request.user == receiver:
            return Response({"error": "You cannot send a friend request to yourself"}, status=status.HTTP_400_BAD_REQUEST)

        if FriendRequest.objects.filter(sender=request.user, receiver=receiver, status='pending').exists():
            return Response({"error": "Friend request already sent"}, status=status.HTTP_400_BAD_REQUEST)

        FriendRequest.objects.create(sender=request.user, receiver=receiver)
        return Response({"message": "Friend request sent"}, status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        request_id = request.data.get('id')
        status = request.data.get('status')

        try:
            friend_request = FriendRequest.objects.get(id=request_id)
        except FriendRequest.DoesNotExist:
            return Response({"error": "Friend request not found"}, status=status.HTTP_404_NOT_FOUND)

        if friend_request.receiver != request.user:
            return Response({"error": "You are not authorized to respond to this friend request"}, status=status.HTTP_403_FORBIDDEN)

        if status not in ['accepted', 'rejected']:
            return Response({"error": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST)

        friend_request.status = status
        friend_request.save()

        return Response({"message": f"Friend request {status}"})

class FriendsListView(generics.ListAPIView):
    serializer_class = UserSerializer

    def get_queryset(self):
        return self.request.user.friends.all()

class PendingFriendRequestsView(generics.ListAPIView):
    serializer_class = UserSerializer

    def get_queryset(self):
        return FriendRequest.objects.filter(receiver=self.request.user, status='pending')
