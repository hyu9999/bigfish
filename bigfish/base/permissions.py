from django.contrib.auth.models import AnonymousUser
from rest_framework import permissions

from bigfish.apps.users.models import BigfishUser


class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.owner


class OnlyTeacherCanChange(permissions.BasePermission):
    def has_permission(self, request, view):
        if isinstance(request.user, AnonymousUser):
            return False
        if view.action in ("update", "partial_update"):
            if request.user.groups.filter(name="teacher").exists() or request.user.identity == 1:
                return True
            else:
                return False
        return True


class OnlyTeacher(permissions.BasePermission):
    def has_permission(self, request, view):
        if isinstance(request.user, AnonymousUser):
            return False
        if request.user.groups.filter(name="teacher").exists() or request.user.identity == 1:
            return True
        else:
            return False


class OnlyAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_staff


class Everyone(permissions.BasePermission):
    def has_permission(self, request, view):
        return True
