from base64 import urlsafe_b64decode
import re
from django.shortcuts import render, redirect

from accounts.forms import UserForm
from accounts.models import User
from django.contrib import messages, auth
from accounts.models import UserProfile
from accounts.utils import send_verification_email #, send_password_reset_email

from vendor.forms import VendorForm

from accounts.utils import detectUser
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied

from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator

from vendor.models import Vendor

#from django.auth.models import au

#Restrict Vendor from accessing other role's accounts
def check_role_vendor(user):
    if user.role == 1:
        return True
    else:
        raise PermissionDenied

#Restrict Customer from accessing other role's accounts
def check_role_customer(user):
    if user.role == 2:
        return True
    else:
        raise PermissionDenied




# Create your views here.
def registerUser(request):
    #form = UserForm
    if request.user.is_authenticated:
        messages.warning(request, 'You are already logged in!')
        return redirect('myAccount')
    elif request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            # password = password.cleaned_data['password']
            # user = form.save(commit=False)
            # user.role = User.CUSTOMER
            # user.set_password(password)
            # user.save()
            # Hashing by creating a user
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username =form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = User.objects.create_user(first_name = first_name, last_name = last_name, username = username, email = email, password = password)
            user.role = User.CUSTOMER
            user.save()

            #Call send verification email function from utils.py
            mail_subject = 'Please, activate your account'
            mail_template = 'accounts/emails/account_verification_email.html'
            send_verification_email(request, user, mail_subject, mail_template)

            messages.success(request, 'Your account has been succesfully created')
            return redirect('registerUser')
    else:
        form = UserForm
    context = {'form':form}
    return render(request, 'accounts/registerUser.html', context)

def registerVendor(request):
    if request.user.is_authenticated:
        messages.warning(request, 'You are already logged in!')
        return redirect('myAccount')
    elif request.method =="POST":
        form = UserForm(request.POST)
        v_form = VendorForm(request.POST, request.FILES)
        if form.is_valid() and v_form.is_valid():
            # Hashing by creating a user
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username =form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = User.objects.create_user(first_name=first_name, last_name=last_name, username=username, email=email, password=password)
            user.role = User.VENDOR
            user.save()
            vendor = v_form.save(commit=False)
            vendor.user = user
            user_profile = UserProfile.objects.get(user=user)
            vendor.user_profile = user_profile
            vendor.save()
            #Call send verification email function from utils.py
            mail_subject = 'Please, activate your account'
            mail_template = 'accounts/emails/account_verification_email.html'
            send_verification_email(request, user, mail_subject, mail_template)

            messages.success(request, 'Your account has been registered successfully! Activate your account from your email and wait for the approval')
            return redirect('registerVendor')
            pass
        else:
            print('invalid form')
            print(form.errors)
    else:
        form = UserForm()
        v_form = VendorForm()
    
    #if request.method == "POST":

    context = {
        'form':form,
        'v_form':v_form
    }
    
    return render(request, 'accounts/registerVendor.html', context)

def activate(request, uidb64, token):
    #Activate the user by setting the is_active status to true
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except(ValueError, OverflowError, TypeError, User.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Congratulations!, Your account has been activated')
        return redirect('myAccount')
    else:
        messages.error(request, 'Invalid Activation Link')
        return redirect('myAccount')



def login(request):
    if request.user.is_authenticated:
        messages.warning(request, 'You are already logged in!')
        return redirect('myAccount')
    elif request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = auth.authenticate(request, email=email, password=password)
        if user is not None:
            auth.login(request, user)
            messages.success(request, 'You are now logged in.')
            return redirect('myAccount')
        else:
            messages.error(request, 'Invalid Credentials')
            return redirect('login')
         

    return render(request, 'accounts/login.html')

def logout(request):
    auth.logout(request)
    messages.info(request, 'You are logged out')
    return redirect('login')

    #return render(request, 'accounts/logout.html')
@login_required(login_url='login')
def myAccount(request):
    user = request.user
    redirectUrl = detectUser(user)
    return redirect(redirectUrl)

# def dashboard(request):

#     return render(request, 'accounts/dashboard.html')
@login_required(login_url='login')
@user_passes_test(check_role_customer)
def custDashboard(request):

    return render(request, 'accounts/custDashboard.html')

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def vendorDashboard(request):
    vendor = Vendor.objects.get(user=request.user)
    # context = {
    #     'vendor':vendor,
    # }
    return render(request, 'accounts/vendorDashboard.html')

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST['email']
        if User.objects.filter(email=email).exists:
            user = User.objects.get(email__exact=email)
            #Call Send password reset email
            mail_subject = 'Reset your password'
            mail_template = 'accounts/emails/reset_password_email.html'
            send_verification_email(request, user, mail_subject, mail_template)
            messages.success(request, 'Password reset link has been sent to your email address')
            return redirect('login')
        else:
            messages.error(request, 'Account does not exist')
            return redirect('forgot_password')

    return render(request, 'accounts/forgot_password.html')

def reset_password_validate(request, uidb64, token):
    # Validate the user by decoding the token and the user pk
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except(ValueError, OverflowError, TypeError, User.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.info(request, 'Please, reset your password')
        return redirect('reset_password')
    else:
        messages.error(request, 'The link has expired')
        return redirect('myAccount')
   

def reset_password(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        if password == confirm_password:
            pk = request.session.get('uid')
            user = User.objects.get(pk=pk)
            user.set_password(password)
            user.is_active
            user.save()
            messages.success(request, 'Password reset successful')
            return redirect('login')
        else:
            messages.error(request, 'Passwords do not match!')
            return redirect('reset_password')

    return render(request, 'accounts/reset_password.html')



    
