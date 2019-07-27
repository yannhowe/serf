from .models import Announcement, SundayAttendance
import datetime
from django.template import Context

now = datetime.datetime.now()


def under_review_count_processor(request):

    total_under_review_count = None

    try:
        announcements_under_review_count = Announcement.objects.filter(publish_end_date__gte=now, under_review=True).count()
    except Announcement.DoesNotExist:
        pass

    try:
        sunday_attendance_under_review_count = SundayAttendance.objects.filter(under_review=True).count()
    except SundayAttendance.DoesNotExist:
        pass

    if announcements_under_review_count or sunday_attendance_under_review_count:
        total_under_review_count = announcements_under_review_count + sunday_attendance_under_review_count

    return {'total_under_review_count': total_under_review_count}
