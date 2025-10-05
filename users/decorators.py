from django.shortcuts import redirect
from functools import wraps

def no_session_required(view_func):
    """
    Decorator that forces the user to NOT be authenticated.
    If authenticated, it redirects them to 'home:home'.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home:home')
        return view_func(request, *args, **kwargs)
    return _wrapped_view