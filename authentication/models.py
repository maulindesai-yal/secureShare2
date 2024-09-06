from django.contrib.auth.models import AbstractBaseUser,PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.base_user import BaseUserManager
import pyotp
import qrcode  # Import qrcode for QR code generation
from io import BytesIO
import base64
import logging

class CustomUserManager(BaseUserManager):
  def create_user(self,email,password=None,**extra_fields):
    if not email:
      raise ValueError('The Email must be set')
    email = self.normalize_email(email)
    user = self.model(email=email, **extra_fields)
    user.set_password(password)

    # Generate the TOTP secret key
    user.secret_key = pyotp.random_base32()
    print(f"Generated secret key: {user.secret_key}")

    user.save()
    return user

  def create_superuser(self,email,password=None,**extra_fields):
    extra_fields.setdefault('is_staff',True)
    extra_fields.setdefault('is_superuser',True)
    extra_fields.setdefault('is_active',True)
    return self.create_user(email,password,**extra_fields)
  
class CustomUser(AbstractBaseUser,PermissionsMixin):
  email = models.EmailField(unique=True)
  first_name = models.CharField(max_length=100)
  last_name = models.CharField(max_length=100)
  is_active = models.BooleanField(default=True)
  is_staff = models.BooleanField(default=False)
  secret_key = models.CharField(max_length=32, null=True, blank=True)

  USERNAME_FIELD = 'email'
  REQUIRED_FIELDS = ['first_name','last_name']
  
  objects = CustomUserManager()

  def get_full_name(self):
    return f"{self.first_name} {self.last_name}"
  
  def __str__(self):
    return self.email
  
  def get_secret_key(self):
    #Ensure that the secret key is always available."""
    print(f"User secret key: {self.secret_key}")
    if not self.secret_key:
      self.secret_key = pyotp.random_base32()
      self.save()

    return self.secret_key
    
  def generate_totp(self):
    """
    Generates a TOTP object for the user based on their secret key.
    """
    return pyotp.TOTP(self.secret_key)
  
  def get_totp_uri(self):
    """
    Generate a TOTP URI for QR code generation.
    """
    totp = self.generate_totp()
    otp_uri = totp.provisioning_uri(name=self.email, issuer_name="SecureShare")
    print(f"TOTP URI: {otp_uri}")  # Debugging line
    return otp_uri

  def generate_qr_code(self):
    """
    Generate a base64-encoded QR code image for the user's TOTP URI.
    """
    otp_uri = self.get_totp_uri()
    qr = qrcode.QRCode(
      version=1,
      error_correction=qrcode.constants.ERROR_CORRECT_L,
      box_size=10,
      border=4,
    )
    qr.add_data(otp_uri)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    qr_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
    return qr_base64
  
  def remove_2fa(self):
    """
    Remove the 2FA setup for the user by clearing the secret key.
    """
    print(f"Removing 2FA for user: {self.email}. Current secret_key: {self.secret_key}")
    logging.debug(f"Removing 2FA for user: {self.email}. Current secret_key: {self.secret_key}")

    # Clear the secret_key
    self.secret_key = None
    
    # Check immediately after setting to None
    print(f"Secret_key set to None, before saving: {self.secret_key}")
    logging.debug(f"Secret_key set to None, before saving: {self.secret_key}")
    
    # Save the user instance
    self.save()

    # Confirm the secret_key is None after saving
    print(f"Updated secret_key after save: {self.secret_key}")
    logging.debug(f"Updated secret_key after save: {self.secret_key}")
