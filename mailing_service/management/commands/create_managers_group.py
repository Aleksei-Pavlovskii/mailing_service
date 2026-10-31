from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Создаёт группу «Менеджеры» с правами просмотра и блокировки"

    def handle(self, *args, **options):
        group, created = Group.objects.get_or_create(name="Менеджеры")

        permissions = Permission.objects.filter(
            content_type__app_label__in=("mailing_service", "users"),
            codename__in=(
                "view_sending",
                "view_recipient",
                "view_sendingattempt",
                "view_user",
                "change_user",
            ),
        )
        group.permissions.set(permissions)

        action = "создана" if created else "обновлена"
        self.stdout.write(self.style.SUCCESS(
            f"Группа «Менеджеры» {action}, назначено прав: {permissions.count()}"
        ))