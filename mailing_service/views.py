from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import cache_page, cache_control, never_cache
from django.views.generic import (
    CreateView, UpdateView, DeleteView, ListView, DetailView, TemplateView,
)

from mailing_service.models import Recipient, Message, Sending, SendingAttempt
from mailing_service.services.sending import send_sending
from users.models import User
from .mixins import ManagerRequiredMixin, OwnerQuerysetMixin, OwnerRequiredMixin
from .permissions import is_manager


# Получатели

class RecipientListView(LoginRequiredMixin, ListView):
    model = Recipient
    template_name = "mailing_service/recipient_list.html"
    context_object_name = "recipients"

    def get_queryset(self):
        if is_manager(self.request.user):
            return Recipient.objects.all()
        return Recipient.objects.filter(owner=self.request.user)


class RecipientDetailView(OwnerQuerysetMixin, DetailView):
    model = Recipient
    template_name = "mailing_service/recipient_detail.html"
    context_object_name = "recipient"


class RecipientCreateView(LoginRequiredMixin, CreateView):
    model = Recipient
    fields = ["full_name", "email", "comment"]
    template_name = "mailing_service/recipient_form.html"
    success_url = reverse_lazy("mailing_service:recipient_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class RecipientUpdateView(OwnerRequiredMixin, UpdateView):
    model = Recipient
    fields = ["full_name", "email", "comment"]
    template_name = "mailing_service/recipient_form.html"
    success_url = reverse_lazy("mailing_service:recipient_list")


class RecipientDeleteView(OwnerRequiredMixin, DeleteView):
    model = Recipient
    template_name = "mailing_service/recipient_delete.html"
    success_url = reverse_lazy("mailing_service:recipient_list")


# Сообщения

@method_decorator(cache_page(60 * 5), name="dispatch")
class MessageListView(ListView):
    model = Message
    template_name = "mailing_service/message_list.html"
    context_object_name = "email_messages"


class MessageDetailView(DetailView):
    model = Message
    template_name = "mailing_service/message_detail.html"
    context_object_name = "email_message"


class MessageCreateView(CreateView):
    model = Message
    fields = ["subject", "body_message"]
    template_name = "mailing_service/message_form.html"
    success_url = reverse_lazy("mailing_service:message_list")


class MessageUpdateView(UpdateView):
    model = Message
    fields = ["subject", "body_message"]
    template_name = "mailing_service/message_form.html"
    success_url = reverse_lazy("mailing_service:message_list")


class MessageDeleteView(DeleteView):
    model = Message
    template_name = "mailing_service/message_delete.html"
    success_url = reverse_lazy("mailing_service:message_list")


# Рассылки

@method_decorator(never_cache, name="dispatch")
class SendingListView(LoginRequiredMixin, ListView):
    model = Sending
    template_name = "mailing_service/sending_list.html"
    context_object_name = "sendings"

    def get_queryset(self):
        if is_manager(self.request.user):
            return Sending.objects.all()
        return Sending.objects.filter(owner=self.request.user)


class SendingDetailView(LoginRequiredMixin, DetailView):
    model = Sending
    template_name = "mailing_service/sending_detail.html"
    context_object_name = "sending"

    def get_queryset(self):
        if is_manager(self.request.user):
            return Sending.objects.all()
        return Sending.objects.filter(owner=self.request.user)


class SendingCreateView(LoginRequiredMixin, CreateView):
    model = Sending
    fields = ["send_until", "message", "recipients"]
    template_name = "mailing_service/sending_form.html"
    success_url = reverse_lazy("mailing_service:sending_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class SendingUpdateView(OwnerRequiredMixin, UpdateView):
    model = Sending
    fields = ["send_until", "message", "recipients"]
    template_name = "mailing_service/sending_form.html"
    success_url = reverse_lazy("mailing_service:sending_list")


class SendingDeleteView(OwnerRequiredMixin, DeleteView):
    model = Sending
    template_name = "mailing_service/sending_delete.html"
    success_url = reverse_lazy("mailing_service:sending_list")


class SendingSendView(LoginRequiredMixin, View):
    """Отправка рассылки по требованию (кнопка на странице детали)."""

    def post(self, request, pk):
        sending = get_object_or_404(Sending, pk=pk)
        if not is_manager(request.user) and sending.owner != request.user:
            raise PermissionDenied("Вы не владелец этой рассылки")

        attempts = send_sending(sending)
        ok = sum(1 for a in attempts if a.status == SendingAttempt.STATUS_SUCCESS)
        messages.success(request, f"Отправлено: {ok} из {len(attempts)}")
        return redirect("mailing_service:sending_detail", pk=sending.pk)


class SendingDisableView(ManagerRequiredMixin, View):
    """Отключение рассылки менеджером."""

    def post(self, request, pk):
        sending = get_object_or_404(Sending, pk=pk)
        sending.status = Sending.STATUS_FINISHED
        sending.save(update_fields=["status"])
        messages.success(request, "Рассылка отключена")
        return redirect("mailing_service:sending_detail", pk=pk)


# Главная и статистика

@method_decorator(cache_page(60 * 10), name="dispatch")
@method_decorator(cache_control(public=True, max_age=300), name="dispatch")
class HomeView(TemplateView):
    template_name = "mailing_service/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_sendings"] = Sending.objects.count()
        context["active_sendings"] = Sending.objects.filter(
            status=Sending.STATUS_STARTED
        ).count()
        context["total_recipients"] = Recipient.objects.count()
        context["success_attempts"] = SendingAttempt.objects.filter(
            status=SendingAttempt.STATUS_SUCCESS
        ).count()
        context["failed_attempts"] = SendingAttempt.objects.filter(
            status=SendingAttempt.STATUS_FAILED
        ).count()
        context["sent_messages"] = context["success_attempts"]
        return context


class StatisticsView(LoginRequiredMixin, TemplateView):
    template_name = "mailing_service/statistics.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        attempts = SendingAttempt.objects.all()
        sendings = Sending.objects.all()
        if not is_manager(self.request.user):
            attempts = attempts.filter(sending__owner=self.request.user)
            sendings = sendings.filter(owner=self.request.user)

        stats = attempts.aggregate(
            total=Count("id"),
            success=Count("id", filter=Q(status=SendingAttempt.STATUS_SUCCESS)),
            failed=Count("id", filter=Q(status=SendingAttempt.STATUS_FAILED)),
        )

        context.update({
            "total_attempts": stats["total"] or 0,
            "success_attempts": stats["success"] or 0,
            "failed_attempts": stats["failed"] or 0,
            "sent_messages": stats["success"] or 0,
        })

        context["per_sending"] = (
            sendings
            .annotate(
                total=Count("attempts"),
                success=Count("attempts", filter=Q(attempts__status=SendingAttempt.STATUS_SUCCESS)),
                failed=Count("attempts", filter=Q(attempts__status=SendingAttempt.STATUS_FAILED)),
            )
            .order_by("-id")
        )
        return context


# Пользователи (менеджер)

class UserListView(ManagerRequiredMixin, ListView):
    model = User
    template_name = "mailing_service/user_list.html"
    context_object_name = "users"


class UserToggleActiveView(ManagerRequiredMixin, View):
    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        if user == request.user:
            messages.error(request, "Нельзя заблокировать себя")
            return redirect("mailing_service:user_list")

        user.is_active = not user.is_active
        user.save(update_fields=["is_active"])
        messages.success(request, "Статус пользователя изменён")
        return redirect("mailing_service:user_list")