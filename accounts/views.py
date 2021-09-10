from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate, logout, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.models import User, ConfirmationCode, VerifyConfirmation
from accounts.forms import UserForm, VerifyConfirmationForm
from accounts.send_confirmation_mail import EmailConfirmation

from wallet.models import(
	CardHolder, 
	BankCard
)

def Sign_Up(request):
	# Initilize the form 
	form = UserForm(request.POST or None) # Post request

	if form.is_valid(): # check if form is valid

		user = form.save(commit=False) # has't yet save the form to db
		
		# process the fields assocaited to the form
		# check if it's a clean data
		username = form.cleaned_data['username']
		password = form.cleaned_data['password']
		email = form.cleaned_data['email']
		
		# set the user password
		user.set_password(password)

		user.save() # save the form to the db

		# authenticate the user with email and password
		user = authenticate(email=email, password=password)

		# check if the user is in the db
		if user is not None:

			# check if user is active
			if user.is_active:

				# log the user in
				login(request, user) # login take 2 args

				# 
				card_holder = CardHolder.objects.filter(user=request.user)

				# Send email confirmation code to user
				EmailConfirmation(request, username, email, password)

				# return user to the verification message pasge
				return render(request, 'accounts/verification_message.html')
				
	context = {
		'form':form # pass the form in the templates
	}
	return render(request, 'accounts/sign-up.html', context)


def Sign_In(request):
	# post user request
	if request.method == 'POST':
		email = request.POST['email']
		password =request.POST['password']

		# authenticate user with email and password
		user = authenticate(email=email, password=password)

		# check if the user exists
		if user is not None:
			
			# check if the user is active
			if user.is_active:

				# log the user in
				login(request, user)

				card_holder = CardHolder.objects.filter(user=request.user)
				back_card = BankCard.objects.filter(user=request.user)
				verified_code = VerifyConfirmation.objects.filter(user=request.user)

				# check if the current page query permeter is next
				if 'next' in request.POST:
					# return the user to the next page
					return redirect(request.POST.get('next'))
				else:
					# return the user to his account profile
					return redirect('profile')

			else:
				# rasie an error because the user is not active
				messages.error(request, f'Your account has been disabled')
				return redirect('sign-in')
		else:
			# rasise an error because the user does not exists
			messages.error(request, f'Invalid login. Please check login credential') 
			return redirect('sign-in')
	# return the sign-in page
	return render(request, 'accounts/sign-in.html')



def Sign_Out(request):
	logout(request) # Log out the requested user
	return redirect('home') # return to the home page
							# after loging user out


def Verify_Account(request):
	code = VerifyConfirmation.objects.filter(user=request.user)
	# Initilize the form 
	form = VerifyConfirmationForm(request.POST or None)

	if form.is_valid(): # check if it's vaild
		entered_code = form.save(commit=False) # has't yet save the form to db

		# process the fields assocaited to the form
		# check if it's a clean data
		verified_code = form.cleaned_data['verified_code']

		# Get the confirmation code that has been sent
		config_code = ConfirmationCode.objects.filter(user=request.user)

		# loop for the confirmed code
		for code in config_code:
			# assigned the confimation to sent
			sent = code.confirmed_code

		# check if the cleaned form data is equal sent
		if verified_code == sent: # if True

			# The entered code is the request user
			entered_code.user = request.user

			# save entered code to db
			entered_code.save()

			# return the requested user to sign in page
			return render(request, 'accounts/verification_pass.html', {'entered_code':entered_code, 'code':code, 'verified_code':verified_code})
		else:
			return render(request, 'accounts/verify_account.html', {'error_message': 'Verification failed. Please check your email to verify the code'})

	# define a context variable for templates
	context = {
		'form':form,
		'code':code
	}
	
	# return the verify account pasge
	return render(request, 'accounts/verify_account.html', context)
