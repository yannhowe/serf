from django.conf.urls import url
from newswire import views
from newswire.views import ProfileList, ProfileCreate, ProfileUpdate, ProfileDelete, RsvpUpdateView, RsvpListView, RsvpListViewRaw, ControlPanelHomeView,  OrderOfServiceList, OrderOfServiceUpdate, BulletinPrintView, BulletinPdfView, BulletinPdfPreviewView, BulletinPdfSendView, GroupListView, GroupCreateView, GroupUpdateView, GroupListView, GroupAttendanceListView, GroupAttendanceCreateView, GroupAttendanceUpdateView, GroupAttendanceListView
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView

urlpatterns = (
    url(r'^$',
        login_required(ControlPanelHomeView.as_view()), name='cp_home'),
    url(r'^rsvp/list/$',
        login_required(RsvpListView.as_view()), name='rsvp_list'),
    url(r'^rsvp/list/raw$',
        login_required(RsvpListViewRaw.as_view()), name='rsvp_list_raw'),
    url(r'^bulletin/$', login_required(ControlPanelHomeView.as_view()),
        name='cp_bulletin_home'),
    url(r'^bulletin/print$', login_required(BulletinPrintView.as_view()),
        name='cp_bulletin_print'),
    #    url(r'^bulletin/print/pdf$', login_required(BulletinPdfView.as_view()),
    #        name='cp_bulletin_print'),
    url(r'^bulletin/pdf/$', login_required(BulletinPdfView.as_view()), name='cp_bulletin_pdf'),
    url(r'^bulletin/pdf/preview/$', login_required(BulletinPdfPreviewView.as_view()), name='cp_bulletin_pdf_preview'),
    url(r'^bulletin/pdf/send/$', login_required(BulletinPdfSendView.as_view()), name='cp_bulletin_pdf_send'),
    url(r'^bulletin/under-review/$', login_required(views.UnderReviewListView.as_view()), name='underreview_list'),
    url(r'^bulletin/under-review/approve/$', login_required(views.UnderReviewApproveView.as_view()), name='underreview_approve'),

    # OrderOfService
    url(r'^bulletin/orderofservice/$',
        views.OrderOfServiceList.as_view(), name='orderofservice_list'),
    url(r'^bulletin/orderofservice/new$',
        views.OrderOfServiceCreate.as_view(), name='orderofservice_new'),
    url(r'^bulletin/orderofservice/edit/(?P<pk>\d+)$',
        views.OrderOfServiceUpdate.as_view(), name='orderofservice_edit'),
    url(r'^bulletin/orderofservice/delete/(?P<pk>\d+)$',
        views.OrderOfServiceDelete.as_view(), name='orderofservice_delete'),

    # Announcement
    url(r'^bulletin/announcement/$',
        views.AnnouncementList.as_view(), name='announcement_list'),
    url(r'^bulletin/announcement/new$',
        views.AnnouncementCreate.as_view(), name='announcement_new'),
    url(r'^bulletin/announcement/edit/(?P<pk>\d+)$',
        views.AnnouncementUpdate.as_view(), name='announcement_edit'),
    url(r'^bulletin/announcement/delete/(?P<pk>\d+)$',
        views.AnnouncementDelete.as_view(), name='announcement_delete'),

    # Category
    url(r'^bulletin/category/$',
        views.CategoryList.as_view(), name='category_list'),
    url(r'^bulletin/category/new$',
        views.CategoryCreate.as_view(), name='category_new'),
    url(r'^bulletin/category/edit/(?P<pk>\d+)$',
        views.CategoryUpdate.as_view(), name='category_edit'),
    url(r'^bulletin/category/delete/(?P<pk>\d+)$',
        views.CategoryDelete.as_view(), name='category_delete'),

    # Event
    url(r'^bulletin/event/$',
        views.EventList.as_view(), name='event_list'),
    url(r'^bulletin/event/new$',
        views.EventCreate.as_view(), name='event_new'),
    url(r'^bulletin/event/edit/(?P<pk>\d+)$',
        views.EventUpdate.as_view(), name='event_edit'),
    url(r'^bulletin/event/delete/(?P<pk>\d+)$',
        views.EventDelete.as_view(), name='event_delete'),

    # Building Fund
    url(r'^bulletin/buildingfund/$',
        views.BuildingFundList.as_view(), name='buildingfund_list'),

    url(r'^bulletin/buildingfundcollection/new$',
        views.BuildingFundCollectionCreate.as_view(), name='buildingfundcollection_new'),
    url(r'^bulletin/buildingfundcollection/edit/(?P<pk>\d+)$',
        views.BuildingFundCollectionUpdate.as_view(), name='buildingfundcollection_edit'),
    url(r'^bulletin/buildingfundcollection/delete/(?P<pk>\d+)$',
        views.BuildingFundCollectionDelete.as_view(), name='buildingfundcollection_delete'),

    # Building Fund Year Pledge
    url(r'^bulletin/buildingfundyearpledge/new$',
        views.BuildingFundYearPledgeCreate.as_view(), name='buildingfundyearpledge_new'),
    url(r'^bulletin/buildingfundyearpledge/edit/(?P<pk>\d+)$',
        views.BuildingFundYearPledgeUpdate.as_view(), name='buildingfundyearpledge_edit'),
    url(r'^bulletin/buildingfundyearpledge/delete/(?P<pk>\d+)$',
        views.BuildingFundYearPledgeDelete.as_view(), name='buildingfundyearpledge_delete'),

    # Building Fund
    url(r'^bulletin/buildingfundyeargoal/new$',
        views.BuildingFundYearGoalCreate.as_view(), name='buildingfundyeargoal_new'),
    url(r'^bulletin/buildingfundyeargoal/edit/(?P<pk>\d+)$',
        views.BuildingFundYearGoalUpdate.as_view(), name='buildingfundyeargoal_edit'),
    url(r'^bulletin/buildingfundyeargoal/delete/(?P<pk>\d+)$',
        views.BuildingFundYearGoalDelete.as_view(), name='buildingfundyeargoal_delete'),

    # Profile
    url(r'^people/summary/$',
        views.ProfileSummary.as_view(), name='profile_summary'),
    url(r'^people/$',
        views.ProfileList.as_view(), name='profile_list'),
    url(r'^people/new$',
        views.ProfileCreate.as_view(), name='profile_new'),
    url(r'^people/edit/(?P<pk>\d+)$',
        views.ProfileUpdate.as_view(), name='profile_edit'),
    url(r'^people/delete/(?P<pk>\d+)$',
        views.ProfileDelete.as_view(), name='profile_delete'),

    # WeeklyVerse
    url(r'^weeklyverse/$',
        views.WeeklyVerseList.as_view(), name='weeklyverse_list'),
    url(r'^weeklyverse/new$',
        views.WeeklyVerseCreate.as_view(), name='weeklyverse_new'),
    url(r'^weeklyverse/edit/(?P<pk>\d+)$',
        views.WeeklyVerseUpdate.as_view(), name='weeklyverse_edit'),
    url(r'^weeklyverse/delete/(?P<pk>\d+)$',
        views.WeeklyVerseDelete.as_view(), name='weeklyverse_delete'),


    # Attendance Input
    url(r'^attendance/summary/$',
        views.AttendanceSummary.as_view(), name='attendance_summary'),
    url(r'^attendance/new$',
        views.AttendanceCreate.as_view(), name='attendance_new'),
    url(r'^attendance/edit/(?P<pk>\d+)$',
        views.AttendanceUpdate.as_view(), name='attendance_edit'),
    url(r'^attendance/delete/(?P<pk>\d+)$',
        views.AttendanceDelete.as_view(), name='attendance_delete'),

    # Group Input
    url(r'^groups/$',
        views.GroupListView.as_view(), name='group_list'),
    url(r'^groups/new$',
        views.GroupCreateView.as_view(), name='group_new'),
    url(r'^groups/edit/(?P<pk>\d+)$',
        views.GroupUpdateView.as_view(), name='group_edit'),
    url(r'^groups/delete/(?P<pk>\d+)$',
        views.GroupDeleteView.as_view(), name='group_delete'),


    # GroupAttendance Input
    url(r'^individual-attendance/$',
        views.GroupAttendanceListView.as_view(), name='groupattendance_list'),
    url(r'^individual-attendance/new$',
        views.GroupAttendanceCreateView.as_view(), name='groupattendance_new'),
    url(r'^individual-attendance/edit/(?P<pk>\d+)$',
        views.GroupAttendanceUpdateView.as_view(), name='groupattendance_edit'),
    url(r'^individual-attendance/delete/(?P<pk>\d+)$',
        views.GroupAttendanceDeleteView.as_view(), name='groupattendance_delete'),
)
