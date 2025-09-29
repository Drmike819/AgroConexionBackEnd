# Nos permite uenviar email
from django.core.mail import send_mail
from django.conf import settings

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

class EmailService:
    # Nos permite llamar a la funcion si necesidad el self, para llamarla de manera mas facil
    @staticmethod
    def send_email(subject, recipient_list, template_name, context):
        html_content = render_to_string(template_name, context)
        text_content = strip_tags(html_content)
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content, # Contenido de texto plano
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=recipient_list
        )
        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=False)