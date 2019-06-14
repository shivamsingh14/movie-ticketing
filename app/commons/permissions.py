from rest_framework import permissions

from app.users.models import User


class AdminPermissions(permissions.BasePermission):
    """
    permission class that return strue if user has admin rights
    """

    def has_permission(self, request, view):
        return request.user.is_admin
