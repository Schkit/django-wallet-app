from django.shortcuts import render, redirect
from django.http import HttpResponse
import json
from accounts.models import User
from friends.models import FriendRequest, FriendsList
from django.contrib.auth.decorators import login_required

# Send Friends Request 
@login_required
def send_friend_request(request, *args, **kwargs):
	user = request.user
	payload = {}

	if request.method == 'POST': # This's a post request
		user_id = request.POST.get("receiver_user_id")
		if user_id:
			receiver = User.objects.get(id=user_id)

			# Return the queryset of friend request
			friend_requests = FriendRequest.objects.filter(
				sender=user, receiver=receiver
			)

			# check for an active friend request
			for request in friend_requests:
				if request.is_active:
					# display a message
					payload['response'] = 'You have already send them a friend request.'
			
			# Create and send a friend request
			friend_requests = FriendRequest(
				sender=user, receiver=receiver
			)
			friend_requests.save() # save the friend request to the database
			# display a message
			payload['response'] = 'Friend request sent.'

			if payload['response'] == None:
				payload['response'] = 'Something went wrong.'
	else:
		payload['response'] = 'Unable to send them a friend request'
	return HttpResponse(json.dumps(payload), content_type='application/json')
#End


# Cancel friend request
@login_required
def cancel_friend_request(request, *args, **kwargs):
	user = request.user
	payload = {}

	if request.method == 'POST':
		user_id = request.POST['receiver_user_id']
		if user_id:
			receiver = User.objects.get(pk=user_id)

			try:
				# Return the queryset of friend request
				friend_requests = FriendRequest.objects.filter(
					sender=user,
					receiver=receiver,
					is_active=True
				)
			except:
				# dispaly a message
				payload['response'] = 'Nothing to cancel. Does not exist'

			# Check for the len of friend request
			if len(friend_requests) > 1:
				# loop to find the friend request and cancelled it
				for request in friend_requests:
					request.cancel()
				payload['response'] = 'Friend request cancelled.'
			else:
				# cancel the first friend request
				friend_requests.first().cancel()
				payload['response'] = 'Friend request cancelled.'
		else:
			# display a messages when the user id is invalid
			payload['response'] = 'Unable to cancel that request, invalid id'

	# This's a httpresponse
	# We're updating the page without loading it using Ajax
	return HttpResponse(json.dumps(payload), content_type='application/json')
#End

# Friend request view
@login_required
def friend_request_view(request, *args, **kwargs):
	context = {} # Empty dictionary
	user = request.user # assign variable user to request.user
	user_id = kwargs.get("user_id") # get the user id

	# assign variable account to User models
	# and get the user model id and assign it to user_id
	try:
		account = User.objects.get(pk=user_id)	
	except:
		return HttpResponse('Something went wrong.')

	# make both account user model and user request.user equal
	if account == user:
		
		# return friend request queryset
		friend_requests = FriendRequest.objects.filter(
			# user id is receiving friend request
			receiver=account, 
			is_active=True
		)
		# defined template variable
		# access the Friend request variable in the template using context
		context = {
			'friend_requests':friend_requests
		}
	else:
		# Unable to view another person request
		return HttpResponse("You can't view another person friend request")
	return render(request, 'friends/friend_request.html', context)
#End

# Accepting Friend request
@login_required
def accept_friend_request(request, *args, **kwargs):
	user = request.user
	payload = {}
	if request.method == 'GET':
		friend_request_id = kwargs.get("friend_request_id")
		if friend_request_id:
			friend_request = FriendRequest.objects.get(
				pk=friend_request_id
			)

			if friend_request.receiver == user:
				if friend_request:
					update_notification = friend_request.accept()
					payload['response'] = 'Friend request accepted.'
				else:
					payload['response'] = 'Something went wrong.'
			else:
				payload['response'] = 'Not your friend request to accept'
		else:
			payload['response'] = 'Unable to accept that friend request'
	return HttpResponse(json.dumps(payload), content_type='application/json')

# End


# Decline Friend request
@login_required
def decline_friend_request(request, *args, **kwargs):
	user = request.user
	payload = {}
	if request.method == "GET":
		friend_request_id = kwargs.get("friend_request_id")
		if friend_request_id:
			friend_request = FriendRequest.objects.get(
				pk=friend_request_id
			)
			if friend_request.receiver == user:
				if friend_request:
					update_notification = friend_request.decline()
					payload['response'] = 'Friend request declined.'

				else:
					payload['response'] = 'Something went wrong.'
			
			else:
				payload['response'] = "Not your friend request to decline."
		
		else:
			payload['response'] = 'Unable to decline that friend request.'

	return HttpResponse(json.dumps(payload), content_type='application/json')
# End


# unfriend a user
@login_required
def unfriend(request, *args, **kwargs):
	user = request.user
	payload = {}
	if request.method == 'POST':
		user_id = request.POST.get('receiver_user_id')
		if user_id:
			try:
				removee = User.objects.get(pk=user_id)
				friend_list = FriendsList.objects.get(user=user)
				friend_list.unfriend(removee)
				payload['response'] = 'Successfully remove a friend.'
			except:
				payload['response'] = 'Somethin went wrong.'
		else:
			payload['response'] = 'There was an error, unable to remove a friend.'
	return HttpResponse(json.dumps(payload), content_type='application/json')
# End

