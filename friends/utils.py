from friends.models import FriendRequest

def get_friend_request_or_false(receiver, sender):
	try:
		return FriendRequest.objects.get(receiver=receiver, sender=sender, is_active=True)
	except FriendRequest.DoesNotExist:
		return False



