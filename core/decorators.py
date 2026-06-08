from django.shortcuts import redirect
from django.contrib import messages

def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_admin:
            messages.error(request, 'Acceso denegado. Se requieren privilegios de administrador.')
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper
