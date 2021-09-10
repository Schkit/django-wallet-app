from django.db import models
import datetime
from accounts.models import User
from django.core.validators import RegexValidator
from django.core.validators import MinValueValidator,MaxValueValidator
import qrcode
from io import BytesIO
from django.core.files import File
from PIL import Image, ImageDraw
from django.urls import reverse


class Main( ): 
    EXPIRE = (
        (2017, '2017'),
        (2018, '2018'),
        (2019, '2019'),
        (2020, '2020'),
        (2021, '2021'),
        (2022, '2022'),
        (2023, '2023'),
        (2024, '2024'),
        (2024, '2024'),
        (2026, '2026'),
        (2027, '2027'),
        (2028, '2028'),
        (2029, '2029'),
        (2030, '2030'),
    )
    bank_card_regex = RegexValidator(regex=r'^\+?1?\d{12}$', message="Numeric Field. Only 12 digits allowed.")
    cvv_regex = RegexValidator(regex=r'^\+?1?\d{3}$', message="Numeric Field. Only 3 digits allowed.")
    card_pass_code = RegexValidator(regex=r'^\+?1?\d{4}$', message="Numeric Field. Only 4 digits allowed.")


# Bank Card Model
class BankCard(models.Model):
    user                = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='user')
    card_number         = models.CharField(validators=[Main.bank_card_regex], max_length=12, unique=True, verbose_name='card number')
    card_amount         = models.PositiveIntegerField(default=10000, verbose_name='account on card')
    expiration_date     = models.IntegerField(choices=Main.EXPIRE, verbose_name='expiration date')
    cvv_number          = models.CharField(validators=[Main.cvv_regex], max_length=3, verbose_name='cvv number')
    hide_card           = models.BooleanField(default=False, verbose_name='hide card')

    def get_absolute_url(self):
        return reverse('card-update', kwargs={'pk': self.pk})
    
    def __str__(self):
        return str(f"{self.user} - {self.card_number}")

# Card Holder Model
class CardHolder(models.Model):
    user                = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='user')
    withdrew            = models.PositiveIntegerField(blank=True, null=True, validators=[MaxValueValidator(5000),MinValueValidator(1)])
    balance             = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    first_name          = models.CharField(max_length=15, blank=True, null=True)
    last_name           = models.CharField(max_length=15, blank=True, null=True)
    timestamp           = models.DateTimeField(auto_now=False, auto_now_add=True)
    hide_balance        = models.BooleanField(default=False)

    def __str__(self):
        return str(self.first_name)

    def get_absolute_url(self):
        return reverse('holder-update', kwargs={'pk': self.pk})

    class Meta:
        ordering = ['-timestamp'] 


# Balance Model
class TopUpBalance(models.Model):
    user                = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    top_up_amount              = models.PositiveIntegerField(blank=True, null=True, validators=[MaxValueValidator(1000000),MinValueValidator(0)])


    def __str__(self):
        return str(f"TopUp - {self.top_up_amount}")

# Withdrew Model
class WithdrewBalance(models.Model):
    user                = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    withdrew_amount              = models.PositiveIntegerField(blank=True, null=True, validators=[MaxValueValidator(1000000),MinValueValidator(0)])


    def __str__(self):
        return str(f"Withdrew - {self.withdrew_amount}")

# Recieved Balance
class ReceivedBalance(models.Model):
    user                = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    recevier_name       = models.CharField(max_length=30)
    amount_recevied     = models.PositiveIntegerField(default=100, validators=[MaxValueValidator(5000)])
    timestamp           = models.DateTimeField(auto_now=False, auto_now_add=True)

    def __str__(self):
        return str(self.amount_recevied)

    class Meta:
        ordering = ['-timestamp']


# Card Pass Code
class CardPassCode(models.Model):
    user                    = models.ForeignKey(User, blank=True, null=True, db_constraint=False, on_delete=models.CASCADE)
    pass_code               = models.CharField(validators=[Main.card_pass_code], max_length=4)

    def __str__(self):
        return str(f"{self.user} - {self.pass_code} - payment code")

# Verified Pass Code
class VerifiedPassCode(models.Model):
    user                    = models.ForeignKey(User, blank=True, null=True, db_constraint=False, on_delete=models.CASCADE)
    verified_pass_code      = models.CharField(validators=[Main.card_pass_code], max_length=4)

    def __str__(self):
        return self.verified_pass_code

# QRCODE Model
class QRCODE(models.Model):
    user                    = models.ForeignKey(User, db_constraint=False, on_delete=models.CASCADE, blank=True, null=True)
    name                    = models.CharField(max_length=200)
    qr_code                 = models.ImageField(upload_to='qr_codes', blank=True, null=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        qrcode_img = qrcode.make(self.name)
        canvas = Image.new('RGB', (290, 290), 'white')
        draw = ImageDraw.Draw(canvas)
        canvas.paste(qrcode_img)
        fname = f'qr_code'+'.jpg'
        buffer = BytesIO()
        canvas.save(buffer, 'PNG')
        self.qr_code.save(fname, File(buffer), save=False)
        canvas.close()
        super().save(*args, **kwargs)







