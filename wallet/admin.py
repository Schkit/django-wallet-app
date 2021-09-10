from django.contrib import admin
from wallet.models import (
BankCard,
CardHolder,
TopUpBalance,
WithdrewBalance,
ReceivedBalance,
CardPassCode,
VerifiedPassCode,
QRCODE
)

# Register your models here.
admin.site.register(BankCard)
admin.site.register(CardHolder)
admin.site.register(TopUpBalance)
admin.site.register(WithdrewBalance)
admin.site.register(ReceivedBalance)
admin.site.register(CardPassCode)
admin.site.register(VerifiedPassCode)
admin.site.register(QRCODE)



