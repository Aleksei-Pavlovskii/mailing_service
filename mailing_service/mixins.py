from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied

from .permissions import is_manager


class ManagerRequiredMixin(LoginRequiredMixin):
    """Доступ только менеджерам. Остальным — 403."""

    def dispatch(self, request, *args, **kwargs):
        if not is_manager(request.user):
            raise PermissionDenied("Доступ только для менеджеров")
        return super().dispatch(request, *args, **kwargs)


class OwnerRequiredMixin(LoginRequiredMixin):
    """Требует логин + владение объектом (obj.owner == request.user)."""

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.owner != self.request.user:
            raise PermissionDenied("Вы не владелец этого объекта")
        return obj


class OwnerQuerysetMixin(LoginRequiredMixin):
    """Пользователь видит только своё, менеджер — всё."""

    def get_queryset(self):
        qs = super().get_queryset()
        if is_manager(self.request.user):
            return qs
        return qs.filter(owner=self.request.user)