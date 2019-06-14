from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from celery.decorators import task

from app.users.models import Booking


@task(name="user_ticket_task")
def user_ticket_task(user_email, ticket_details):
    context = {
        'movie': ticket_details['slot']['movie']['name'],
        'date': ticket_details['slot']['date'],
        'time': ticket_details['slot']['slot'],
        'seats': ticket_details['seats_booked'],
        'audi': ticket_details['slot']['audi']['name']
    }
    send_mail(
            subject='Ticket Confirmation',
            message=render_to_string('ticketConfirmation.txt', context),
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user_email],
            html_message=render_to_string('ticketConfirmation.html', context),
            fail_silently=False,
        )


@task(name="send_cancelled_ticket_task")
def send_cancelled_ticket_task(user, ticket_details):
    context = {
        'movie': ticket_details['slot']['movie']['name'],
        'date': ticket_details['slot']['date'],
        'time': ticket_details['slot']['slot'],
        'seats': ticket_details['seats_booked'],
        'audi': ticket_details['slot']['audi']['name']
    }
    recipient_users = []
    recipient_users.append(user)
    send_mail(
        subject='Ticket Cancellation',
        message=render_to_string('ticketCancellation.txt', context),
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=recipient_users,
        html_message=render_to_string('ticketCancellation.html', context),
        fail_silently=False,
    )
