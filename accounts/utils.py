from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from accounts.models import User
from wallet.models import CardHolder, BankCard
from accounts.forms import AccountProfileForm
from friends.models import FriendsList, FriendRequest
from friends.utils import get_friend_request_or_false
from friends.friend_request_status import FriendRequestStatus
from django.conf import settings
from django.http import HttpResponse



# Allowing user to change their password
from django.contrib.auth.views import PasswordChangeView


@login_required
def account_profile(request, *args, **kwargs):
    context = {} 
    if request.method == 'POST': # this is a post request

        form = AccountProfileForm(
            request.POST, # accept post request
            request.FILES, # accept files such as jpg etc
            instance=request.user # accept the current user instance
        )

        if form.is_valid(): # validates the form
            form.save() # save the form to the db
            return redirect('profile') # redirect the user to the same route
        else:
            return render(request, 'accounts/accounts_profile.html', {'error_message': f'Email already exists in our system', 'form':form})

    else:
        form = AccountProfileForm(instance=request.user) # fill the form the user info

    holder = get_object_or_404(CardHolder, user=request.user)
    card = get_object_or_404(BankCard, user=request.user)


    context = {
        'form':form, # to access the form with the template
        'holder':holder,
        'card':card
    }

    # render the user to the account profile page 
    return render(request, 'accounts/accounts_profile.html', context)


@login_required
def account_view(request, *args, **kwargs):
    """
    - Logic here is kind of tricky
        is_self
        is_friend
            -1: NO_REQUEST_SENT
            0: THEM_SENT_TO_YOU
            1: YOU_SENT_TO_THEM
    """
    context = {}
    user_id = kwargs.get("user_id")
    try:
        account = User.objects.get(pk=user_id)
    except:
        return HttpResponse("Something went wrong.")
    if account:
        context['id'] = account.id
        context['username'] = account.username
        context['email'] = account.email
        context['profile_image'] = account.profile_image.url
        context['hide_email'] = account.hide_email

        try:
            friend_list = FriendsList.objects.get(user=account)
        except FriendsList.DoesNotExist:
            friend_list = FriendsList(user=account)
            friend_list.save()
        friends = friend_list.friends.all()
        context['friends'] = friends
    
        # Define template variables
        is_self = True
        is_friend = False
        request_sent = FriendRequestStatus.NO_REQUEST_SENT.value # range: ENUM -> friend/friend_request_status.FriendRequestStatus
        friend_requests = None
        user = request.user
        if user.is_authenticated and user != account:
            is_self = False
            if friends.filter(pk=user.id):
                is_friend = True
            else:
                is_friend = False
                # CASE1: Request has been sent from THEM to YOU: FriendRequestStatus.THEM_SENT_TO_YOU
                if get_friend_request_or_false(sender=account, receiver=user) != False:
                    request_sent = FriendRequestStatus.THEM_SENT_TO_YOU.value
                    context['pending_friend_request_id'] = get_friend_request_or_false(
                        sender=account, receiver=user
                    ).id

                # CASE2: Request has been sent from YOU to THEM: FriendRequestStatus.YOU_SENT_TO_THEM
                elif get_friend_request_or_false(sender=user, receiver=account) != False:
                    request_sent = FriendRequestStatus.YOU_SENT_TO_THEM.value
                
                # CASE3: No request sent from YOU or THEM: FriendRequestStatus.NO_REQUEST_SENT
                else:
                    request_sent = FriendRequestStatus.NO_REQUEST_SENT.value
        
        elif not user.is_authenticated:
            is_self = False
        else:
            try:
                friend_requests = FriendRequest.objects.filter(receiver=user, is_active=True)
            except:
                pass
            
        # Set the template variables to the values
        context['is_self'] = is_self
        context['is_friend'] = is_friend
        context['request_sent'] = request_sent
        context['friend_requests'] = friend_requests
        context['BASE_URL'] = settings.BASE_URL
    return render(request, "accounts/account_view.html", context)
# End


@login_required
def search(request, *args, **kwargs):
    context = {} # empty dictionary

    if request.method == 'GET': # this is a get request

        holder = get_object_or_404(CardHolder, user=request.user)
        # assign the request method to a variable
        search_query = request.GET.get('q', None)
        

        # 
        if search_query and len(search_query):

            

            # search for username
            search_results = User.objects.filter(username__icontains=search_query)

            user = request.user # assign variable user to request.user
            users = [] # empty list

            # loop for user in the search results 
            for user in search_results:

                users.append((user, False)) # this is for friends system

            context['users'] = users # define a context variable for templates
        
        context['holder'] = holder
    
    # return the search page routes
    return render(request, 'accounts/search.html', context)
















