from rest_framework import permissions

class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Check if the requesting user is the owner of the object
        return obj.user == request.user
