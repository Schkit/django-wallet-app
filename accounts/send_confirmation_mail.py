import string
import random
from accounts.models import User, ConfirmationCode
from django.core.mail import send_mail
from django.conf import settings

def EmailConfirmation(request, emailto, usrname, passwrd):
	chars = ''.join((string.digits)) # charaters of strings
	config_code = ''.join(random.choice(chars) for x in range(6)).upper()
	save_code = ConfirmationCode.objects.filter(user=request.user).create(confirmed_code=config_code)
	save_code.user = request.user
	save_code.save()
	content = 'Hello, '+usrname + '\nThanks For Signing Up On Schkit Pay\nUsername :' +usrname+'\nVerification Code: '+config_code+'\n\nAbout Schkit Pay:\n\n'+'Schkit Pay is a web platform or system where user will be able to maintain his wallet\nand he will be able to use his wallet money to recharge his mobile and can\neven transfer funds/wallet balance to other users.\nYou will also be able to add money to wallet through cash card.\n\nWe hope everything goes well, and once again, if you need help, please dont hesitate to get in touch.\n\nContact us: schkit01@gmail.com\n\n'
	send_mail(
    	"Welcome To Schkit Pay!",
    	content,
        settings.EMAIL_HOST_USER,
    	[usrname], 
    	fail_silently=False
   	)
