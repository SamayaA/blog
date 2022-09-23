from rest_framework import permissions

class UserPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        if view.action in ['retrieve', 'list']:
            return True
        elif view.action in ['update', 'partial_update', 'destroy', 'create', 'delete']:
            return request.user.is_authenticated
        else:
            return False
                                                                                                
    def has_object_permission(self, request, view, obj):
        # Deny actions on objects if the user is not authenticated
        if view.action in ['retrieve', 'list']:
            return True
        elif view.action in ['update', 'partial_update', 'destroy', 'delete']:
            return request.user.is_authenticated
        else:
            return False