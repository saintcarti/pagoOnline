from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.shortcuts import redirect

def admin_required(view_func=None, redirect_url='index-page'):
    """
    Decorador que verifica si el usuario es admin/staff
    """
    def check_admin(user):
        return user.is_authenticated and user.is_staff
    
    actual_decorator = user_passes_test(
        check_admin,
        login_url=redirect_url
    )
    
    if view_func:
        return actual_decorator(view_func)
    return actual_decorator


def role_required(*roles, redirect_url='index-page'):
    """
    Decorador para verificar roles específicos
    Ejemplo: @role_required('admin', 'bodeguero')
    """
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            user = request.user
            if user.is_authenticated and (user.is_staff or getattr(user, 'rol', None) in roles):
                return view_func(request, *args, **kwargs)
            messages.error(request, "No tienes permisos para acceder a esta sección")
            return redirect(redirect_url)
        return wrapper
    return decorator