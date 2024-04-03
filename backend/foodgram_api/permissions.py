from rest_framework.permissions import SAFE_METHODS, BasePermission


class AuthorStaffOrReadOnly(BasePermission):
    """
    Разрешение на изменение только
    для служебного персонала и автора.
    Остальным только чтение объекта.
    """

    def has_object_permission(
        self, request, view, obj
    ) -> bool:
        return (
            request.method in SAFE_METHODS
            or request.user.is_authenticated
            and request.user.is_active
            and (request.user == obj.author or request.user.is_staff)
        )


class AdminOrReadOnly(BasePermission):
    """
    Разрешение на создание и изменение только для админов.
    Остальным только чтение объекта.
    """

    def has_object_permission(self, request, view) -> bool:
        return (
            request.method in SAFE_METHODS
            or request.user.is_authenticated
            and request.user.is_active
            and request.user.is_staff
        )
