from django.contrib.auth.decorators import login_required
from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.hashers import make_password
from authentication.models import CustomUser
from home.models import Document,Share
from django.db.models import Q
import pyotp

# Create your views here.

def register(request):
  if request.method == 'POST':
    first_name = request.POST.get('first_name')
    last_name = request.POST.get('last_name')
    email = request.POST.get('email')
    password = request.POST.get('password')
    confirm_password = request.POST.get('confirm_password')

    if password != confirm_password:
      return render(request,'registration/register.html',{'error':'Passwords do not match'})
    
    if CustomUser.objects.filter(email=email).exists():
      return render(request,'registration/register.html',{'error':'Email already exists'})
    
    
    user = CustomUser(
      first_name=first_name,
      last_name=last_name,
      email=email,
      password=make_password(password),
      is_active=True
    )
    user.save()
    return redirect ('login') 
  return render (request,'registration/register.html')


def user_login(request):
  if request.method == 'POST':
    email = request.POST.get('email')
    password = request.POST.get('password')
    user = authenticate(request,email=email,password=password)
    
    print(f"Login attempt: email={email}, authenticated={user is not None}")
    if user is not None:
      login(request,user)
      if user.secret_key is None:
        return redirect("dashboard")
      else:
        return redirect('verify_2fa')
    else:
      return render(request, 'registration/login.html',{'error':'Invalid credentials'})
  
  return render (request,'registration/login.html')


def logout_user(request):
  auth_logout(request)
  messages.success(request, "You have been logged out successfully.")
  return redirect ('login')

@login_required
def setup_2fa(request):
  user = request.user
  user.get_secret_key()
  # Generate QR code for the user
  qr_code = user.generate_qr_code()

  # Debugging line to check secret key
  print(f"User secret key: {user.secret_key}")
  return render(request, 'registration/setup_2fa.html', {'qr_code': qr_code, 'secret_key': user.secret_key})

@login_required
def verify_2fa(request):
  
  if request.method == 'POST':
    code = request.POST.get('code')
    user = request.user

    if user.secret_key:
      totp = pyotp.TOTP(user.secret_key)
      if totp.verify(code):
        # Successful verification
        return redirect('dashboard')  # Redirect to the desired page
      else:
        # Failed verification
        return render(request, 'registration/verify_2fa.html', {'error': 'Invalid code'})
    else:
      return redirect('dashboard')  # Redirect to the desired page
  return render(request, 'registration/verify_2fa.html')

@login_required
def remove_2fa_view(request):
  if request.method == 'POST':
    user = request.user
    user.remove_2fa()
    return redirect('dashboard')  # Redirect to a suitable page

  return render(request, 'registration/remove_2fa.html')