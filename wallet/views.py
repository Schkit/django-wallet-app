from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from accounts.models import User, VerifyConfirmation, ConfirmationCode
from friends.models import (
	FriendsList,
	FriendRequest
)
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.db.models import F
from django.core.mail import send_mail
from decimal import Decimal


from wallet.models import (
	BankCard, 
	CardHolder, 
	CardPassCode,
	VerifiedPassCode,
	ReceivedBalance

)

from wallet.forms import (
	CardHolderDetailForm,
	BankCardForm,
	CardPassCodeForm,
	TopUpBalanceForm,
	WithdrewBalanceForm,
	VerifiedPassCodeForm,
)


@login_required
def card_holder_detail(request, *args, **kwargs):
	context = {}
	card_holder = CardHolder.objects.filter(user=request.user)
	confired_code = ConfirmationCode.objects.filter(user=request.user)
	verified_code = VerifyConfirmation.objects.filter(user=request.user)
	form = CardHolderDetailForm(
		request.POST
		or None
	)
	if form.is_valid():
		holder = form.save(commit=False)
		first_name = form.cleaned_data['first_name']
		last_name = form.cleaned_data['last_name']
		holder.user = request.user
		holder.save()
		return render(request, 'wallet/balance.html', {'card_holder':card_holder})
	context = {
		'form':form,
		'card_holder':card_holder,
		'confired_code':confired_code,
		'verified_code':verified_code
	}
	return render(request, 'wallet/card_holder_detail.html', context)


@login_required
def balance(request):
	context = {}
	verified_code = VerifyConfirmation.objects.filter(user=request.user)
	confired_code = ConfirmationCode.objects.filter(user=request.user)
	bank_card = BankCard.objects.filter(user=request.user)
	card_holder = CardHolder.objects.filter(user=request.user)
	card_pass_code = CardPassCode.objects.filter(user=request.user)
	verified_pass_code = VerifiedPassCode.objects.filter(user=request.user)
	context = {
		'verified_code':verified_code,
		'confired_code':confired_code,
		'bank_card':bank_card,
		'card_holder':card_holder,
		'card_pass_code':card_pass_code,
		'verified_pass_code':verified_pass_code
	}
	return render(request, 'wallet/balance.html', context)


@login_required
def add_bank_card(request):
	context = {}
	card_holder = CardHolder.objects.filter(user=request.user)
	bank_card = BankCard.objects.filter(user=request.user)

	form = BankCardForm(
		request.POST
		or None
	)
	if form.is_valid():
		card = form.save(commit=False)
		card_number = form.cleaned_data['card_number']
		expiration_date = form.cleaned_data['expiration_date']
		cvv_number = form.cleaned_data['cvv_number']
		card.user = request.user
		card.save()
		return redirect('pay-code')
	
	context = {
		'form':form,
		'bank_card':bank_card,
		'card_holder':card_holder
	}

	return render(request , 'wallet/bank_card.html', context)



@login_required
def add_payment_pass_code(request):
	context = {}
	bank_card = BankCard.objects.filter(user=request.user)
	card_holder = CardHolder.objects.filter(user=request.user)
	form = CardPassCodeForm(
		request.POST
		or None
	)
	if form.is_valid():
		code = form.save(commit=False)
		pass_code = form.cleaned_data['pass_code']
		code.user = request.user
		code.save()
		return redirect('balance')
	context = {
		'form':form,
		'card_holder':card_holder,
		'bank_card':bank_card
	}
	return render(request, 'wallet/payment_pass_code.html', context)


@login_required
def top_up_balance(request, *args, **kwargs):
	context = {}
	confirmed_code = ConfirmationCode.objects.filter(user=request.user)
	bank_card = BankCard.objects.filter(user=request.user)
	card_holder = CardHolder.objects.filter(user=request.user)

	form = TopUpBalanceForm(
		request.POST
		or None
	)

	if form.is_valid():
		top_up = form.save(commit=False)
		top_up_amount = form.cleaned_data['top_up_amount']

		for card in bank_card:
			amount_on_card = card.card_amount # default amaount 10,000 USD

		if amount_on_card >= top_up_amount:
			BankCard.objects.filter(id__in=bank_card).update(
				card_amount=F('card_amount') - top_up_amount
			)
			CardHolder.objects.filter(id__in=card_holder).update(
				balance=F('balance') + top_up_amount
			)
			top_up.user = request.user
			top_up.save()

			
			return render(request, 'wallet/top_up_success.html', {'card_holder':card_holder, 'bank_card':bank_card, 'confirmed_code':confirmed_code, 'top_up_amount':top_up_amount})
		
		else:
			messages.error(request, f'Amount exceeds available card amount')
			return redirect('top-up')

	context = {
		'form':form,
		'card_holder':card_holder,
		'bank_card':bank_card
	}
	return render(request, 'wallet/top_up.html', context)




@login_required
def withdrew_balance(request, *args, **kwargs):
	context = {}
	confirmed_code = ConfirmationCode.objects.filter(user=request.user)
	card_holder = CardHolder.objects.filter(user=request.user)
	bank_card = BankCard.objects.filter(user=request.user)

	form = WithdrewBalanceForm(
		request.POST
		or None
	)

	if form.is_valid():
		withdrew = form.save(commit=False)
		withdrew_amount = form.cleaned_data['withdrew_amount']

		for holder in card_holder:
			holder_balance = holder.balance

		if holder_balance >= withdrew_amount:
			CardHolder.objects.filter(id__in=card_holder).update(
				balance=F('balance') -  withdrew_amount
			)
			BankCard.objects.filter(id__in=bank_card).update(
				card_amount=F('card_amount') + withdrew_amount
			)
			withdrew.user = request.user
			withdrew.save()

			return render(request, 'wallet/withdrew_success.html', {'withdrew_amount':withdrew_amount, 'bank_card':bank_card, 'card_holder':card_holder})
		
		else:
			messages.error(request, f'Amount entered exceeds available Balance')
			return redirect('withdrew')

	context = {
		'form':form,
		'bank_card':bank_card,
		'card_holder':card_holder
	}

	return render(request, 'wallet/withdrew.html', context)


@login_required
def transfer(request, *args, **kwargs):
	context = {}
	confirmed_code = ConfirmationCode.objects.filter(user=request.user)
	bank_card = BankCard.objects.filter(user=request.user)
	card_holder = CardHolder.objects.filter(user=request.user)


	user=request.user

	# Transfer code logic
	card_pass_code = VerifiedPassCode.objects.filter(user=request.user)
	
	form = VerifiedPassCodeForm(
		request.POST or None

	)

	if form.is_valid():
		pass_code = form.save(commit=False)
		verified_pass_code = form.cleaned_data['verified_pass_code']
		code = CardPassCode.objects.filter(user=request.user)

		for pay_code in code:
			sent = pay_code.pass_code

		if verified_pass_code == sent:
			pass_code.user = request.user
			pass_code.save()
		else:
			messages.error(request, f'Invalid code. Please check pass code')
			return redirect('transfer')
	# End

	
	if request.method == 'POST':
		friend_list = FriendsList.objects.get(user=request.user)
		friends = friend_list.friends.all()

		for user_name in friends:
			u_name = user_name.user

		
			username = request.POST['username']
			amount = request.POST['amount']

			sendName = User.objects.get(username=request.user) # Sender
			receiverName = User.objects.get(username=u_name) # Receiver
			receivers = CardHolder.objects.filter(user=receiverName) # Receiver

			if u_name == sendName:
				messages.error(request, f'Unable to transfer to yourself')
				return redirect('transfer')

			

			for receiver in receivers:
				holder_name = receiver.first_name + ' ' + receiver.last_name
				receiverBalance = Decimal(receiver.balance) + Decimal(amount)

			for holder in card_holder:
				holder_balance = holder.balance

			if Decimal(holder_balance) >= Decimal(amount):
				CardHolder.objects.filter(id__in=card_holder).update(
					balance=F('balance') - Decimal(amount)
				)
				CardHolder.objects.filter(id__in=receivers).update(
					balance=F('balance') + Decimal(amount)
				)
				user = User.objects.get(cardholder__in=receivers)
				receiverEmail=user.email


				rec = ReceivedBalance.objects.filter(user=user).create(
					amount_recevied=Decimal(amount), recevier_name=str(receiverName)
				)
				rec.user=user
				rec.save()

				# send_mail('You Have Received '+str(amount)+'¥ In Your Schkit Pay','Hello, '+str(receiverName)+'!\n'+str(sendName)+' has sent $'+str(amount)+' to your Schkit Pay\nUpdated Wallet Balance :$'+str(receiverBalance)+'\n\n\nContact us: schkit01@gmail.com\n', "(Schkit Pay) Schkit pay mitchellsherman01@gmail.com", [receiverEmail])
				return render(request, 'wallet/transfer_success.html', {'bank_card':bank_card, 'card_holder':card_holder, 'amount':amount})
			
			else:
				messages.error(request, f'Amount entered exceeds available Balance')
				return redirect('transfer')

		else:
			messages.error(request, f'You must be friends before you can transfer')
			return redirect('transfer')


	
	context = {
		'form':form,
		'bank_card':bank_card,
		'card_holder':card_holder,
	}
	return render(request, 'wallet/transfer.html',context)