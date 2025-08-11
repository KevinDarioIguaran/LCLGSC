import os
from datetime import timedelta
import time

from django.conf import settings
from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils._os import safe_join
from django.utils.timezone import now
from django.views.decorators.http import require_POST
from django.contrib.auth import update_session_auth_hash
from django.views.decorators.csrf import csrf_protect
from django.contrib.admin.models import LogEntry
from django.contrib.auth import authenticate

import logging
logger = logging.getLogger(__name__)

from users.models import CustomUser



User = get_user_model()


@login_required
def show_account_view(request):
    return render(request, "account/profile/show_account.html")



def login_view(request):
    if request.user.is_authenticated:
        return redirect('users:show_account')

    errors = {}
    if request.method == "POST":
        user_input = request.POST.get("identifier")
        password = request.POST.get("password")

        user = None

        if user_input and user_input:
            try:
                user = CustomUser.objects.get(code=(user_input))
            except CustomUser.DoesNotExist:
                errors["identifier"] = "Usuario no encontrado o contraseña incorrecta."
        else:
            errors["identifier"] = "Debes ingresar tu código de usuario."

        if user:
            if user.check_password(password):
                login(request, user)
                return redirect("users:show_account")
            else:
                errors["password"] = "Usuario no encontrado o contraseña incorrecta."
    return render(request, "account/signin.html", {"errors": errors})


def signup_view(request):
    errors = {}
    if request.method == "POST":
        identifier = request.POST.get("identifier")
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        secret_code = request.POST.get("secret_code", "").strip()
        print(f"Identifier: {identifier}, First Name: {first_name}, Last Name: {last_name}, Secret Code: {secret_code}")

        user = None
        valid = False

        try:
            if not (identifier and first_name and last_name and secret_code):
                print("Missing required fields")
                raise ValueError()

            user = CustomUser.objects.get(code=identifier)

            if user.first_name.lower() != first_name.lower():
                print("First name does not match")
                raise ValueError()

            if user.last_name.lower() != last_name.lower():
                print("Last name does not match")
                raise ValueError()

            if user.secret_code != secret_code:
                print("Secret code does not match")
                raise ValueError()

            valid = True

        except (CustomUser.DoesNotExist, ValueError):
            pass


        if user and valid:
            request.session['set_password_user_code'] = user.code
            return redirect('users:set_password')
        else:
            errors["non_field"] = "No pudimos validar tus datos. Intenta de nuevo."

    return render(request, "account/signup.html", {"errors": errors})



def set_password(request):
    errors = {}
    user_code = request.session.get('set_password_user_code')

    if not user_code:
        return redirect("users:login")

    try:
        user = CustomUser.objects.get(pk=user_code)
    except CustomUser.DoesNotExist:
        request.session.pop('set_password_user_code', None)
        return redirect("users:login")

    if user.has_usable_password():
        request.session.pop('set_password_user_code', None)
        return redirect("users:login")

    if request.method == "POST":
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        if not password1 or not password2:
            errors["password"] = ["Debes ingresar y confirmar la contraseña."]
        elif password1 != password2:
            errors["password"] = ["Las contraseñas no coinciden."]
        else:
            try:
                validate_password(password1, user=user)
                user.set_password(password1)
                user.save()
                request.session.pop('set_password_user_code', None)

                try:
                    # loguear
                    login(request, user)
                    return redirect("users:show_account") 
                except Exception:
                    return redirect("users:show_account")

            except ValidationError as e:
                errors["password"] = e.messages

    return render(request, "account/set_password.html", {"errors": errors})


@login_required
@require_POST
def change_password_view(request):
    if request.headers.get("x-requested-with") != "XMLHttpRequest":
        return redirect('users:show_account')

    errors = {}
    user = request.user
    current_password = request.POST.get("current_password")
    new_password1 = request.POST.get("new_password1")
    new_password2 = request.POST.get("new_password2")

    if not current_password or not new_password1 or not new_password2:
        errors["password"] = "Todos los campos son obligatorios."
    elif not user.check_password(current_password):
        errors["current_password"] = "Tu contraseña actual es incorrecta."
    elif new_password1 != new_password2:
        errors["new_password"] = "Las nuevas contraseñas no coinciden."
    else:
        try:
            validate_password(new_password1, user=user)
            user.set_password(new_password1)
            user.save()
            update_session_auth_hash(request, user)
            return JsonResponse({'success': True, 'redirect_url': reverse('users:show_account')})
        except ValidationError as e:
            errors["new_password"] = e.messages

    return JsonResponse({'success': False, 'errors': errors})



@login_required
@require_POST
def delete_account_view(request):
    password = request.POST.get("password")
    user = request.user

    if not password or not user.check_password(password):
        return JsonResponse({"success": False, "error": "Contraseña incorrecta."}, status=400)

    photo_path = user.photo.path if user.photo and user.photo.name else None

    try:
        logout(request)
        user.delete()

        if photo_path and os.path.isfile(photo_path):
            if os.path.commonpath([photo_path, settings.MEDIA_ROOT]) == settings.MEDIA_ROOT:
                os.remove(photo_path)
    except Exception:
        return JsonResponse({"success": False, "error": "Error interno al eliminar cuenta."}, status=500)

    return JsonResponse({"success": True, "redirect_url": reverse("home:home")})

