from django.shortcuts import render
from django.utils.deprecation import MiddlewareMixin
from django.utils import timezone

from blocks.models import ActiveSite, Hours, DayBlock, VacationBlock, WeekendDay


class BlocksMiddleware(MiddlewareMixin):
    """
    Middleware that blocks access if the site is not active according to:
        - service hours
        - weekend rules
        - specific blocked days
        - vacation periods
    """

    EXEMPT_PATHS = ['/administracion/', '/static/', '/media/', '/favicon.ico']

    def process_request(self, request):
        if any(request.path.startswith(p) for p in self.EXEMPT_PATHS):
            return None

        try:
            if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser or getattr(request.user, 'is_seller', False)):
                return None
        except Exception:
            pass


        active_site = ActiveSite.objects.first()
        if not active_site:
            return None  

        now = timezone.localtime()
        today = now.date()
        current_time = now.time()
        weekday = now.weekday() 

        if weekday in [5, 6]: 
            weekend_day = WeekendDay.objects.filter(active_site=active_site).first()
            if weekend_day:
                weekend_hours_qs = weekend_day.hours.all()
                if weekend_hours_qs.exists():
                    in_service = any(h.start_time <= current_time <= h.end_time for h in weekend_hours_qs)
                    if not in_service:
                        return render(request, "pages/blocks/no-service.html", status=503)
                else:
                    return render(request, "pages/blocks/no-service.html", status=503)
            else:
                return render(request, "pages/blocks/no-service.html", status=503)
        else:
            hours_qs = Hours.objects.filter(active_site=active_site)
            print(hours_qs)
            if hours_qs.exists():
                in_service = any(h.start_time <= current_time <= h.end_time for h in hours_qs)
                if not in_service:
                    return render(request, "pages/blocks/no-service.html", status=503)
            else:
                return render(request, "pages/blocks/no-service.html", status=503)

        if DayBlock.objects.filter(active_site=active_site, day=today).exists():
            return render(request, "pages/blocks/no-service.html", status=503)

        if VacationBlock.objects.filter(
            active_site=active_site,
            start_date__lte=today,
            end_date__gte=today
        ).exists():
            return render(request, "pages/blocks/no-service.html", status=503)
        return None