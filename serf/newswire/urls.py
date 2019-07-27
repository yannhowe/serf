from django.conf.urls import include, url
from newswire import views
from newswire.views import BulletinHomePageView, ProfileDetailFrontEndView, ProfileUpdateFrontEndView, RsvpUpdateView, RsvpListView, RsvpListViewRaw, AttendanceFrontEndCreate, AttendanceFrontEndUpdate, AttendanceFrontEndDelete, AnnouncementFrontEndCreate, AnnouncementFrontEndUpdate, AnnouncementFrontEndDelete, BulletinPdfView, UnderReviewFrontEndListView, EventListFrontEndView
from django.contrib.auth.decorators import login_required

from django.views.generic import TemplateView

urlpatterns = (
    url(r'^bulletin/$', BulletinHomePageView.as_view(), name='home'),

    url(r'^bulletin/events/$', EventListFrontEndView.as_view(), name='events_front_end'),

    url(r'^bulletin/rsvp/update/$',
        login_required(RsvpUpdateView.as_view()), name='update-rsvp'),
    url(r'^bulletin/send/bulletin/',
        login_required(views.send_bulletin), name='send-bulletin'),

    url(r'^accounts/profile/update/$',
        login_required(ProfileUpdateFrontEndView.as_view()), name='profile_front_end_update'),
    url(r'^accounts/profile/$',
        login_required(ProfileDetailFrontEndView.as_view()), name='profile_front_end_detail'),

    url(r'^bulletin/submit/$',
        login_required(UnderReviewFrontEndListView.as_view()), name='under_review_front_end'),
    url(r'^bulletin/submit/attendance/$',
        login_required(AttendanceFrontEndCreate.as_view()), name='attendance_front_end_new'),
    url(r'^bulletin/submit/announcement/$',
        login_required(AnnouncementFrontEndCreate.as_view()), name='announcement_front_end_new'),

    url(r'^bulletin/announcement/update/(?P<pk>\d+)$',
        login_required(views.AnnouncementFrontEndUpdate.as_view()), name='announcement_front_end_update'),
    url(r'^bulletin/attendance/update/(?P<pk>\d+)$',
        login_required(views.AttendanceFrontEndUpdate.as_view()), name='attendance_front_end_update'),
    url(r'^bulletin/announcement/delete/(?P<pk>\d+)$',
        login_required(views.AnnouncementFrontEndDelete.as_view()), name='announcement_front_end_delete'),
    url(r'^bulletin/attendance/delete/(?P<pk>\d+)$',
        login_required(views.AttendanceFrontEndDelete.as_view()), name='attendance_front_end_delete'),

    url(r'^bulletin/pdf/$', BulletinPdfView.as_view(), name='bulletin_pdf'),
    url(r'^bulletin/404/$', TemplateView.as_view(template_name='404.html')),
    url(r'^bulletin/500/$', TemplateView.as_view(template_name='500.html')),
)
