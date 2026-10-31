from django.contrib import admin

from mailing_service.models import (
    Recipient, Message, Sending, SendingAttempt,
)


@admin.register(Recipient)
class RecipientAdmin(admin.ModelAdmin):
    list_display = ("email", "full_name", "owner")
    search_fields = ("email", "full_name")


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("subject",)
    search_fields = ("subject",)


@admin.register(Sending)
class SendingAdmin(admin.ModelAdmin):
    list_display = ("first_sent_at", "send_until", "status", "owner", "message")
    list_filter = ("status",)
    search_fields = ("message__subject",)


@admin.register(SendingAttempt)
class SendingAttemptAdmin(admin.ModelAdmin):
    list_display = ("attempted_at", "status", "sending")
    list_filter = ("status",)