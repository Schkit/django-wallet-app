from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from accounts.models import User
from django.db.models import F
from .forms import (
	CardHolderSettingForm, 
	CardHolderForm,
	BankCardUpdateForm,
	VerifiedPassCodeForm,
)
from wallet.models import (
	CardHolder, 
	BankCard, 
	QRCODE,
	CardPassCode,
	VerifiedPassCode,
	ReceivedBalance
)

from django.contrib import messages
from decimal import Decimal


@login_required
def cardholder_update(request, pk):
	context = {}
	holder = get_object_or_404(CardHolder, id=pk, user=request.user)

	if request.method == 'POST':
		form = CardHolderSettingForm(request.POST, instance=holder)
		if form.is_valid():
			form.save()
			messages.success(request, f"Card holder's has been updated")
			return render(request, 'wallet/cardholder_update.html', {'form':form, 'holder':holder})
	else:
		form = CardHolderSettingForm(instance=holder)
	context = {
		'form':form,
		'holder':holder
	}
	return render(request, 'wallet/cardholder_update.html', context)


@login_required
def bankcard_update(request, pk):
	context = {}
	card = get_object_or_404(BankCard, id=pk, user=request.user)
	
	holder = get_object_or_404(CardHolder, user=request.user)
	bank_card = BankCard.objects.filter(user=request.user)

	if request.method == 'POST':
		form = BankCardUpdateForm(request.POST, instance=card)
		if form.is_valid():
			form.save()
			messages.success(request, 'Your bank card has been updated')
			return render(request, 'wallet/bankcard_update.html', {'form':form, 'card':card, 'holder':holder, 'bank_card':bank_card})
	else:
		form = BankCardUpdateForm(instance=card)

	context = {
		'form':form,
		'card':card,
		'bank_card':bank_card,
		'holder':holder
	}

	return render(request, 'wallet/bankcard_update.html', context)


@login_required
def delete_bank_card(request, pk):
	context = {}
	card = get_object_or_404(BankCard, id=pk, user=request.user)
	holder = CardHolder.objects.filter(user=request.user)
	bank_card = BankCard.objects.filter(user=request.user)

	if request.method == 'POST':
		card.delete()
		form = BankCardUpdateForm(request.POST or None)
		if form.is_valid():
			delete_card = form.save(commit=False)
			delete_card.user = request.user
			delete_card.save()
		return redirect('bank-card')

	context = {
		'card':card,
		'bank_card':bank_card,
		'holder':holder,
		'form':form,
	}
	return render(request, 'wallet/bankcard_update.html', context)



@login_required
def scan_to_transfer(request, *args, **kwargs):
	obj = QRCODE.objects.get(id=18)
	card_holder = CardHolder.objects.filter(user=request.user)

	context = {
        "obj": obj,
        'card_holder':card_holder
    }
	return render(request, 'wallet/scan_to_transfer.html', context)


@login_required
def payee(request, pk,  *args, **kwargs):
	context = {}

	holder = get_object_or_404(CardHolder, id=pk, user=request.user)
	card_holder = CardHolder.objects.filter(user=request.user)

	user=request.user

	if request.method == 'POST':
		try:
			amount = request.POST['amount']

			sendName = User.objects.get(username=request.user) # Sender
			receiverName = User.objects.get(username=request.user) # Receiver
			receiver = CardHolder.objects.filter(user=receiverName) # Receiver

		except:
			messages.error(request, f'Username and Email does not exists')
			return redirect('payee')

		for holder in card_holder:
			holderBalance = holder.balance

		if Decimal(holderBalance) >= Decimal(amount) and sendName == receiverName:
			CardHolder.objects.filter(id__in=card_holder).update(balance=F('balance') - Decimal(amount))
			CardHolder.objects.filter(id__in=receiver).update(balance=F('balance') + Decimal(amount))
			user = User.objects.get(cardholder__in=receiver)
			rec = ReceivedBalance.objects.filter(user=user).create(amount_recevied=Decimal(amount), recevier_name=str(sendName))
			rec.user=user
			rec.save()
			return render(request, 'wallet/transfer_success.html', {'card_holder':card_holder, 'amount':amount})
		
		else:
			messages.error(request, f'Amount entered exceeds available Balance')
			return redirect('payee')

	context = {
		'card_holder':card_holder,
		'holder':holder
	}
	return render(request, 'wallet/payee.html',context)



