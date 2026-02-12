from rest_framework.permissions import BasePermission, SAFE_METHODS


class DemoUserReadOnly(BasePermission):
    """
    El usuario demo solo puede leer (GET, HEAD, OPTIONS).
    """

    def has_permission(self, request, view):

        user = request.user

        if not user or not user.is_authenticated:
            return True

        if getattr(user, "email", "").lower() == "demo@almapasteleria.com":
            return request.method in SAFE_METHODS

        return True
