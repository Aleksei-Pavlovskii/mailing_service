from django.core.mail import send_mail
from django.utils import timezone
from mailing_service.models import SendingAttempt, Sending


def send_sending(sending):
    attempts = []
    for recipient in sending.recipients.all():
        try:
            send_mail(
                subject=sending.message.subject,
                message=sending.message.body_message,
                from_email=None,
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

    SendingAttempt.objects.bulk_create(attempts)

    if sending.first_sent_at is None:
        sending.first_sent_at = timezone.now()
    sending.status = (
        Sending.STATUS_FINISHED
        if sending.send_until and timezone.now() >= sending.send_until
        else Sending.STATUS_STARTED
    )
    sending.save(update_fields=["first_sent_at", "status"])
    return attempts
