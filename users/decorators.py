from django.shortcuts import redirect
from functools import wraps

def no_session_required(view_func):
    """
    Decorador que obliga a que el usuario NO esté autenticado.
    Si está autenticado, lo redirige a 'home:home'.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home:home')
        return view_func(request, *args, **kwargs)
    return _wrapped_view