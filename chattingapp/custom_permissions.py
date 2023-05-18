from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied
from .models import User


# class IsRegisteredUser(BasePermission):
#     def has_permission(self, request, view):
#         # print(request.method)
#         user_Registerdid = request.data['Registerd_id']
#         if User.objects.filter(registered_userid = user_Registerdid).exists():
#             return True
#         else:
#             raise PermissionDenied('You are not authorized to perform this action.')

class IsRegisteredUser(BasePermission):
    def has_permission(self, request, view):
        user_Registerdid = request.data.get('Registerd_id')
        if user_Registerdid:
            current_user = User.objects.get(registered_userid = request.data.get('Registerd_id'))
            if current_user.email == request.data.get('email'):
                return True
            else:
                raise PermissionDenied('You are not authorized to perform this action.')
        else:
            # Registerd_id parameter is not present in the request data
            # Allow the request to continue without checking if the user is registered
            return True


class isLoginedUser(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            user = User.objects.get(id = request.user.id)
            if user.is_active is True and user.is_verified is True:
                return True
            else:
                raise PermissionDenied('You are not authorized to perform this action.')   
        raise PermissionDenied('You are not authorized to perform this action.')

class IsCurrentUser(BasePermission):
    def has_permission(self, request, view):
        user_Registerdid = request.data.get('Registerd_id')
        if user_Registerdid:
            if User.objects.filter(registered_userid = user_Registerdid).exists():
                return True
            else:
                raise PermissionDenied('You are not authorized to perform this action.')  
        else:
            return True        

          