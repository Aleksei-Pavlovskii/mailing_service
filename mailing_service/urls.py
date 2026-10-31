from django.urls import path

from mailing_service.views import (
    HomeView,
    StatisticsView,
    SendingListView, SendingDetailView, SendingCreateView,
    SendingUpdateView, SendingDeleteView, SendingSendView, SendingDisableView,
    MessageListView, MessageDetailView, MessageCreateView,
    MessageUpdateView, MessageDeleteView,
    RecipientListView, RecipientDetailView, RecipientCreateView,
    RecipientUpdateView, RecipientDeleteView,
    UserListView, UserToggleActiveView,
)

app_name = "mailing_service"

urlpatterns = [
    # Главная / статистика
    path("", HomeView.as_view(), name="home"),
    path("statistics/", StatisticsView.as_view(), name="statistics"),

    # Рассылки
    path("sendings/", SendingListView.as_view(), name="sending_list"),
    path("sendings/create/", SendingCreateView.as_view(), name="sending_create"),
    path("sendings/<int:pk>/", SendingDetailView.as_view(), name="sending_detail"),
    path("sendings/<int:pk>/update/", SendingUpdateView.as_view(), name="sending_update"),
    path("sendings/<int:pk>/delete/", SendingDeleteView.as_view(), name="sending_delete"),
    path("sendings/<int:pk>/send/", SendingSendView.as_view(), name="sending_send"),
    path("sendings/<int:pk>/disable/", SendingDisableView.as_view(), name="sending_disable"),

    # Сообщения
    path("messages/", MessageListView.as_view(), name="message_list"),
    path("messages/create/", MessageCreateView.as_view(), name="message_create"),
    path("messages/<int:pk>/", MessageDetailView.as_view(), name="message_detail"),
    path("messages/<int:pk>/update/", MessageUpdateView.as_view(), name="message_update"),
    path("messages/<int:pk>/delete/", MessageDeleteView.as_view(), name="message_delete"),

    # Получатели
    path("recipients/", RecipientListView.as_view(), name="recipient_list"),
    path("recipients/create/", RecipientCreateView.as_view(), name="recipient_create"),
    path("recipients/<int:pk>/", RecipientDetailView.as_view(), name="recipient_detail"),
    path("recipients/<int:pk>/update/", RecipientUpdateView.as_view(), name="recipient_update"),
    path("recipients/<int:pk>/delete/", RecipientDeleteView.as_view(), name="recipient_delete"),

    # Менеджер: пользователи
    path("manage/users/", UserListView.as_view(), name="user_list"),
    path("manage/users/<int:pk>/toggle-active/", UserToggleActiveView.as_view(), name="user_toggle_active"),
]