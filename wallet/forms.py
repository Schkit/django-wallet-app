from django import forms
from accounts.models import User
from wallet.models import (
    CardHolder,
    BankCard,
    CardPassCode,
    TopUpBalance,
    WithdrewBalance,
    VerifiedPassCode,
   
)

# Bank Card Detail Form
class CardHolderDetailForm(forms.ModelForm):
	first_name = forms.CharField(required=True)
	last_name = forms.CharField(required=True) 

	class Meta:
		model = CardHolder
		fields = ['first_name', 'last_name']


class CardHolderForm(forms.ModelForm):
    user = forms.CharField()

    class Meta:
        model = CardHolder
        fields = ['user']


# Back Card Form
class BankCardForm(forms.ModelForm):
    
    class Meta:
        model = BankCard
        fields = ['card_number', 'expiration_date', 'cvv_number']


# Payment Pass Code Form
class CardPassCodeForm(forms.ModelForm):

    class Meta:
        model = CardPassCode
        fields = ['pass_code']


# Top Up Balance Form
class TopUpBalanceForm(forms.ModelForm):
    top_up_amount = forms.IntegerField()

    class Meta:
        model = TopUpBalance
        fields = ['top_up_amount']



# Withdrew Balance Form
class WithdrewBalanceForm(forms.ModelForm):
    withdrew_amount = forms.IntegerField()

    class Meta:
        model = WithdrewBalance
        fields = ['withdrew_amount']


# Transfer Pass Code Form
class VerifiedPassCodeForm(forms.ModelForm):

    class Meta:
        model = VerifiedPassCode
        fields = ['verified_pass_code']


# Card Holder Setting Form
class CardHolderSettingForm(forms.ModelForm):
    
    class Meta:
        model = CardHolder
        fields = ['first_name', 'last_name', 'hide_balance']

    def save(self, commit=True):
        update = super(CardHolderSettingForm, self).save(commit=False)
        update.first_name = self.cleaned_data['first_name']
        update.last_name = self.cleaned_data['last_name']
        update.hide_balance = self.cleaned_data['hide_balance']

        if commit:
            update.save()
        return update


# Bank Card Update Form
class BankCardUpdateForm(forms.ModelForm):
    class Meta:
        model = BankCard
        fields = ['card_number', 'expiration_date', 'cvv_number', 'hide_card']

    def save(self, commit=False):
        card = super(BankCardUpdateForm, self).save(commit=True)
        card.card_number = self.cleaned_data['card_number']
        card.expiration_date = self.cleaned_data['expiration_date']
        card.cvv_number = self.cleaned_data['cvv_number']
        card.hide_card = self.cleaned_data['hide_card']

        if commit:
            card.save()
        return card




        
    







    

    




