from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from users.user_forms.create_user_admin import CustomUserCreationForm, CustomUserChangeForm
from django.utils.translation import gettext_lazy as _
from django.contrib.admin.models import LogEntry
from django.contrib.contenttypes.models import ContentType


class AppListFilter(admin.SimpleListFilter):
    title = _('Aplicación')
    parameter_name = 'app_label'

    def lookups(self, request, model_admin):
        apps = ContentType.objects.values_list('app_label', flat=True).distinct()
        return [(app, app) for app in apps]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(content_type__app_label=self.value())
        return queryset


admin.site.site_header = "Panel de Cooperativa Luis Carlos"
admin.site.site_title = "Panel de Cooperativa Luis Carlos"
admin.site.index_title = "Bienvenido al panel"


@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    list_display = (
        'action_time', 'get_user_code', 'content_type',
        'object_repr', 'get_action_flag', 'change_message',
    )
    list_filter = ('action_flag', AppListFilter, 'user__code', 'content_type')
    search_fields = ('object_repr', 'change_message', 'user__code')
    date_hierarchy = 'action_time'

    def get_user_code(self, obj):
        return obj.user.code if obj.user else "—"
    get_user_code.short_description = 'Código del usuario'

    def get_action_flag(self, obj):
        return {
            1: "Creó",
            2: "Editó",
            3: "Eliminó"
        }.get(obj.action_flag, "¿?")
    get_action_flag.short_description = 'Acción'


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser

    list_display = (
        'code', 'first_name', 'last_name', 'is_seller', 'is_active', 'is_staff',
    )
    search_fields = (
        'code', 'first_name', 'last_name', 'cooperative_name', 'secret_code'
    )
    ordering = ('code',)

    readonly_fields = (
        'secret_code', 'last_login'
    )

    fieldsets = (
        (None, {'fields': ('code', 'password')}),
        ('Información personal', {
            'fields': (
                'first_name', 'last_name', 'is_seller', 'cooperative_name', 'cooperative_logo'
            )
        }),
        ('Finanzas', {
            'fields': ('credit', 'debt')
        }),
        ('Código de verificación', {'fields': ('secret_code',)}),
        ('Permisos', {
            'fields': (
                'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'
            )
        }),
        ('Fechas importantes', {'fields': ('last_login',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'code', 'first_name', 'last_name', 'is_seller', 'cooperative_name',
                'credit', 'debt', 'password1', 'password2', 'is_active', 'is_staff', 'is_superuser'
            )
        }),
    )
