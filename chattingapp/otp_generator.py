import random, datetime, time, os
from django.utils import timezone
from .models import User, OTP_Checking
from django.conf import settings
from rest_framework import exceptions
from django.core.mail import send_mail

def send_otp(email):
    otp = random.randint(100000, 999999) # generate a random 6-digit OTP
    subject = 'Your OTP for logging in to our website'
    message = f'Your OTP is: {otp}. Please use this code to log in to our website.'
    from_email = settings.EMAIL_HOST
    recipient_list = [email]
    send_mail(subject, message, from_email, recipient_list)
    user = User.objects.filter(email = email).first()
    if user:

        if OTP_Checking.objects.filter(user_id = user.id).exists():
                user_otp = OTP_Checking.objects.filter(user_id = user.id).first()
                user_otp.OTP = otp
                user_otp.created_time = timezone.now() 
                user_otp.is_verified = False
                user_otp.save()      
        else:
            saver = OTP_Checking()
            saver.user_id = user
            saver.OTP = otp
            saver.save()
    else:
        raise exceptions.AuthenticationFailed('inavild email')

    
def send_message(email, new_subject, new_message):
    subject = new_subject
    message = new_message
    from_email = settings.EMAIL_HOST
    recipient_list = [email]
    send_mail(subject, message, from_email, recipient_list)




