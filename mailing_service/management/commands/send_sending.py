from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from mailing_service.models import Sending, SendingAttempt


def send_sending(sending):
    """Отправляет рассылку всем получателям. Попытки пишет одним batch."""
    attempts = []

    for recipient in sending.recipients.all():
        try:
            send_mail(
                subject=sending.message.subject,
                message=sending.message.body_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient.email],
                fail_silently=False,
            )
            attempts.append(SendingAttempt(
                sending=sending,
                status=SendingAttempt.STATUS_SUCCESS,
                server_response="250 OK",
            ))
        except Exception as exc:
            attempts.append(SendingAttempt(
                sending=sending,
                status=SendingAttempt.STATUS_FAILED,
                server_response=str(exc),
            ))

    if attempts:
        SendingAttempt.objects.bulk_create(attempts)

    if sending.first_sent_at is None:
        sending.first_sent_at = timezone.now()

    if sending.send_until and timezone.now() >= sending.send_until:
        sending.status = Sending.STATUS_FINISHED
    else:
        sending.status = Sending.STATUS_STARTED

    sending.save(update_fields=["first_sent_at", "status"])
    return attempts