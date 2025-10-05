from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class ActiveSite(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name=_("Nombre del sitio activo"),
        default="Sitio" 
    )

    class Meta:
        verbose_name = _("Sitio activo")
        verbose_name_plural = _("Sitio activo")
        ordering = ['name']


    def __str__(self):
        return self.name

class WeekendDay(models.Model):
    active_site = models.ForeignKey(
        ActiveSite,
        on_delete=models.CASCADE,
        related_name="weekend_days",
        verbose_name=_("Sitio activo")
    )
    day_of_week = models.IntegerField(
        choices=[
            (5, _("Sábado")),
            (6, _("Domingo")),
        ],
        verbose_name=_("Día del fin de semana")
    )

    class Meta:
        verbose_name = _("Día del fin de semana")
        verbose_name_plural = _("Días del fin de semana")
        ordering = ['day_of_week']
        unique_together = ('active_site', 'day_of_week') 

    def __str__(self):
        return f"Día del fin de semana: {self.get_day_of_week_display()}"

class WeekendDayHour(models.Model):
    weekend_day = models.ForeignKey(
        WeekendDay,
        on_delete=models.CASCADE,
        related_name="hours",
        verbose_name=_("Día de fin de semana")
    )
    start_time = models.TimeField(_("Hora de inicio"))
    end_time = models.TimeField(_("Hora de fin"))

    class Meta:
        verbose_name = _("Hora de servicio de fin de semana")
        verbose_name_plural = _("Horas de servicio de fin de semana")
        ordering = ['start_time']
        unique_together = ('weekend_day', 'start_time', 'end_time')

    def clean(self):
        if self.start_time >= self.end_time:
            raise ValidationError(_("La hora de inicio debe ser anterior a la hora de fin."))

    def __str__(self):
        return f"{self.weekend_day}: {self.start_time} - {self.end_time}"

class Hours(models.Model):
    active_site = models.ForeignKey(
        ActiveSite,
        on_delete=models.CASCADE,
        related_name="hours",
        verbose_name=_("Sitio activo")
    )
    start_time = models.TimeField(_("Hora de inicio"))
    end_time = models.TimeField(_("Hora de fin"))


    def clean(self):
        if self.start_time >= self.end_time:
            raise ValidationError(_("La hora de inicio debe ser anterior a la hora de fin."))

    def __str__(self):
        return f"Hora de {self.start_time} a {self.end_time}"


class DayBlock(models.Model):
    active_site = models.ForeignKey(
        ActiveSite,
        on_delete=models.CASCADE,
        related_name="day_blocks",
        verbose_name=_("Sitio activo")
    )
    day = models.DateField(_("Día bloqueado"))

    class Meta:
        verbose_name = _("Bloqueo por día")
        verbose_name_plural = _("Bloqueos por días")
        ordering = ['day']
        unique_together = ('active_site', 'day') 

    def clean(self):
        if self.day < timezone.now().date():
            raise ValidationError(_("La fecha de bloqueo no puede ser en el pasado."))

    def __str__(self):
        return f"Bloqueo día {self.day}"


class VacationBlock(models.Model):
    active_site = models.ForeignKey(
        ActiveSite,
        on_delete=models.CASCADE,
        related_name="vacation_blocks",
        verbose_name=_("Sitio activo"),
    )
    
    start_date = models.DateField(_("Fecha de inicio"))
    end_date = models.DateField(_("Fecha de fin"))

    class Meta:
        verbose_name = _("Bloqueo por vacaciones")
        verbose_name_plural = _("Bloqueos por vacaciones")
        ordering = ['start_date']

    def clean(self):
        if self.start_date >= self.end_date:
            raise ValidationError(_("La fecha de inicio debe ser anterior a la fecha de fin."))

    def __str__(self):
        return f"Vacaciones: {self.start_date} - {self.end_date}"