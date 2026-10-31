from django.db import models

from django.conf import settings


class Recipient(models.Model):
    """Получатель рассылки"""
    email = models.EmailField(
        unique=True,
        verbose_name='Email'
    )
    full_name = models.CharField(
        max_length=100,
        verbose_name='Ф.И.О.')
    comment = models.TextField(
        verbose_name='Комментарий',
        blank=True,
        null=True
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="recipients",
        verbose_name="Владелец",
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = 'Получатель'
        verbose_name_plural = 'Получатели'
        ordering = ['email']


class Message(models.Model):
    """Сообщение"""
    subject = models.CharField(
        max_length=200,
        verbose_name='Тема'
    )
    body_message = models.TextField(verbose_name='Тело письма')

    def __str__(self):
        return self.subject

    class Meta:
        verbose_name = 'тема'
        verbose_name_plural = 'темы'
        ordering = ['subject']


class Sending(models.Model):
    """Рассылка"""
    STATUS_CREATED = "created"
    STATUS_STARTED = "started"
    STATUS_FINISHED = "finished"

    STATUS_CHOICES = [
        (STATUS_CREATED, "Создана"),
        (STATUS_STARTED, "Запущена"),
        (STATUS_FINISHED, "Завершена"),
    ]

    first_sent_at = models.DateTimeField(
        'Дата и время первой отправки',
        null=True,
        blank=True,
    )
    send_until = models.DateTimeField(
        verbose_name='Дата и время окончания отправки'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_CREATED,
        verbose_name='Статус'
    )
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        verbose_name="Сообщение"
    )
    recipients = models.ManyToManyField(
        Recipient,
        verbose_name="Получатели"
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sendings",
        verbose_name="Владелец",
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.message.subject


class SendingAttempt(models.Model):
    """Попытка рассылки"""
    STATUS_SUCCESS = "success"
    STATUS_FAILED = "failed"
    STATUS_CHOICES = [
        (STATUS_SUCCESS, "Успешно"),
        (STATUS_FAILED, "Не успешно"),
    ]

    attempted_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата и время попытки"
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="success",
        verbose_name="Статус"
    )
    server_response = models.TextField(
        blank=True,
        verbose_name="Ответ почтового сервера"
    )
    sending = models.ForeignKey(
        Sending,
        on_delete=models.CASCADE,
        related_name="attempts",
        verbose_name="Рассылка"
    )

    def __str__(self):
        return f'Попытка #{self.pk}: {self.sending} — {self.get_status_display()}'
