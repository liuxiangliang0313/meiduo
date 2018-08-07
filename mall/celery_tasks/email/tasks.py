# coding:utf8
from django.core.mail import send_mail
from celery_tasks.main import app


@app.task
def send_verify_email(subject, message, from_email, recipient_list, html_message):
    send_mail(subject,
              message,
              from_email,
              recipient_list,
              html_message=html_message)
