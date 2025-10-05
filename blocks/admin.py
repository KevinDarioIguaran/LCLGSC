from django.contrib import admin
from .models import ActiveSite, DayBlock, VacationBlock, Hours, WeekendDay, WeekendDayHour

class HoursInline(admin.TabularInline):
    model = Hours
    extra = 1

class DayBlockInline(admin.TabularInline):
    model = DayBlock
    extra = 1

class VacationBlockInline(admin.TabularInline):
    model = VacationBlock
    extra = 1

class WeekendDayHourInline(admin.TabularInline):
    model = WeekendDayHour
    extra = 1

@admin.register(ActiveSite)
class ActiveSiteAdmin(admin.ModelAdmin):
    list_display = ["id", "name"]
    inlines = [HoursInline, DayBlockInline, VacationBlockInline]
    search_fields = ["id", "name"]

@admin.register(WeekendDay)
class WeekendDayAdmin(admin.ModelAdmin):
    list_display = ["id", "active_site", "day_of_week"]
    inlines = [WeekendDayHourInline]
    list_filter = ["active_site", "day_of_week"]
    search_fields = ["id", "active_site__name"]
