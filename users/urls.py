from django.urls import path
from .views import SignupView, LoginView, UserSearchView, FriendRequestView, FriendsListView, PendingFriendRequestsView

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('search/', UserSearchView.as_view(), name='search'),
    path('friend-request/', FriendRequestView.as_view(), name='friend_request'),
    path('friends/', FriendsListView.as_view(), name='friends_list'),
    path('pending-requests/', PendingFriendRequestsView.as_view(), name='pending_requests'),
]
