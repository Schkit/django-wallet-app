from django import forms
from django.forms import ModelForm
from django.core.validators import RegexValidator
from .models import User, VerifyConfirmation, ConfirmationCode

# Registration Form
class UserForm(forms.ModelForm):
	password 				= forms.CharField(widget=forms.PasswordInput, validators=[RegexValidator(regex=r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[$@$!%*?&])[A-Za-z\d$@$!%*?&]{8,20}', message="Password should contain Minimum 8 characters, at least 1 Uppercase Alphabet, 1 Lowercase Alphabet, 1 Number and 1 Special Character")])
	username				= forms.CharField(min_length=5)
	email 					= forms.EmailField(required=True)
	
	
	# Checking if email already exists
	# User email is unique
	# Two user cannot have the same email
	def clean_email(self):
		email = self.cleaned_data['email']
		try:
			user = User.objects.filter(email=email).exists()
		except User.DoesNotExist:
			raise forms.ValidationError("This email is already registered with us")
		return email

	# accessing the user model and the feilds associated it
	class Meta:
		model = User
		fields = ['username', 'email', 'password']



# Verifing the confirmation code form
class VerifyConfirmationForm(forms.ModelForm):

	# accessing the user model and the feilds associated it
	class Meta:
		model = VerifyConfirmation
		fields = ['verified_code']



# Accout Profile Form
class AccountProfileForm(forms.ModelForm):

	# accessing the user model and the feilds associated it
	class Meta:
		model = User
		fields = ['username', 'email', 'hide_email', 'profile_image']


	# validating the email
	# email is unique
	# user cannot have the same email
	def clean_email(self):
		email = self.cleaned_data['email']
		try:
			user = User.objects.exclude(pk=self.instance.pk).get(email=email)
		except User.DoesNotExist:	
			return email
		raise forms.ValidationError(f'Email {email} is already in use')

	# overriding the save method to save the fields to the db
	# cleaning the data
	def save(self, commit=True):
		user = super(AccountProfileForm, self).save(commit=False)
		user.username = self.cleaned_data['username']
		user.email = self.cleaned_data['email']
		user.hide_email = self.cleaned_data['hide_email']
		user.profile_image = self.cleaned_data['profile_image']

		if commit:
			user.save()
		return user





		
