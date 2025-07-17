from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from core.settings import EMAIL_HOST_USER
from rest_framework import status
from rest_framework.response import Response
import sys

def send_reset_password_email(email, link):
    try:
        subject = 'Reset Your Password'
        from_email = EMAIL_HOST_USER

        try:
            html_content = render_to_string('password_reset_email.html', {
                'email': email,
                'link': link,
            })
        except Exception as template_error:
            print(f"TEMPLATE ERROR: {template_error}")
            raise

        msg = EmailMultiAlternatives(subject, html_content, from_email, [email])
        msg.attach_alternative(html_content, "text/html")
        msg.send()

        return True
    except Exception as e:
        import traceback
        print("EMAIL SEND ERROR:")
        traceback.print_exc()
        return False
    
# Email send to Contact Support
def send_contact_support_email(data):
    try:
        subject = f"Support Request: {data.get('reason')}"  # Changed from subject, since it's not in your payload
        from_email = EMAIL_HOST_USER
        to_email = [data.get("email")]  # You can also use another admin email

        # HTML content
        html_content = render_to_string('contact_support.html', {
            'first_name': data.get('first_name'),
            'last_name': data.get('last_name'),
            'reason': data.get('reason'),
            'email': data.get('email'),
            'message': data.get('message'),
        })

        # Create email
        msg = EmailMultiAlternatives(subject, html_content, from_email, [from_email])
        msg.attach_alternative(html_content, "text/html")
        msg.send()

        return True

    except Exception as e:
        import traceback
        print("EMAIL SEND ERROR:")
        traceback.print_exc()
        return False
