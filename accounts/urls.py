from django.urls import path
from accounts import views as account_view
from accounts import utils as utils_view

# Allow user to change their password
from django.contrib.auth.views import PasswordChangeView



urlpatterns = [
    path('profile/', utils_view.account_profile, name='profile'),
    path('change-password/', PasswordChangeView.as_view(template_name='accounts/password-change.html'), name='password-change'),
    path('search/', utils_view.search, name='search'),    
    path('sign-out/', account_view.Sign_Out, name='sign-out'),
    path('sign-in/', account_view.Sign_In, name='sign-in'),
    path('sign-up/', account_view.Sign_Up, name='sign-up'),
    path('<user_id>', utils_view.account_view, name='account-view'),
    path('verify-account/', account_view.Verify_Account, name='verify-account')
]


