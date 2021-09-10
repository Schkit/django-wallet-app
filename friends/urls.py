from django.urls import path
from friends.views import (
	send_friend_request,
	cancel_friend_request,
	friend_request_view,
	accept_friend_request,
	unfriend,
	decline_friend_request
)

app_name = 'friends'

urlpatterns = [
	path('accept_friend_request/<friend_request_id>/', accept_friend_request, name='accept-request'),
	path('cancel_friend_request/', cancel_friend_request, name='cancel-friend-request'),
	path('decline_friend_request/<friend_request_id>/', decline_friend_request, name='decline-request'),
	path('friend_request_view/<user_id>', friend_request_view, name='friend-request'),
	path('send_friend_request/', send_friend_request, name='send-friend-request'),
	path('unfriend/', unfriend, name='unfriend')
]

