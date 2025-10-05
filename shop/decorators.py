from django.shortcuts import redirect
from functools import wraps

def seller_required(view_func):
    """
    Decorador que obliga a que el usuario sea vendedor (is_seller=True).
    Si no, lo redirige a 'home:home'.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('users:login')
        if not getattr(request.user, 'is_seller', False):
            return redirect('home:home')
        return view_func(request, *args, **kwargs)
    return _wrapped_view
