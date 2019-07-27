# -*- coding: utf-8 -*-
from newswire.forms import ProfileForm, ProfileFrontEndForm, UserFormFrontEndForm, OrderOfServiceForm, AnnouncementForm, CategoryForm, EventForm, AttendanceForm, WeeklyVerseForm, AttendanceForm, AttendanceFormFrontEnd, AnnouncementFormFrontEnd, BuildingFundCollectionForm, BuildingFundYearPledgeForm, BuildingFundYearGoalForm, ExtendedGroupForm, GroupAttendanceForm
from newswire.models import Announcement, Category, OrderOfService, Announcement, Event, Signup, Profile, Relationship, WeeklyVerse, SundayAttendance, BuildingFundCollection, BuildingFundYearPledge, BuildingFundYearGoal, ExtendedGroup, GroupAttendance

from datetime import datetime, timedelta
import datetime

from django.utils import timezone

from django import template
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User, Group
from django.core import mail, serializers
from django.core.files.storage import default_storage
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.urls import reverse
from django.db.models import Q, Sum, F, When, Case
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.template import RequestContext
from django.template.loader import select_template, get_template, render_to_string
from django.template.response import TemplateResponse
from django.template import Context
from django.utils import timezone
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView, DetailView, FormView
from django.views.generic.base import ContextMixin
from django.urls import reverse_lazy
import os
import json
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from constance import config
from weasyprint import HTML, CSS

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import redirect

from django.core.mail import EmailMessage


def get_today():
    return datetime.datetime(timezone.now().year, timezone.now().month, timezone.now().day)


def get_now():
    return timezone.now()


def get_future(days_into_future):
    return get_now() + datetime.timedelta(days_into_future)


def get_upcoming_birthdays(person_list, days, from_date=get_today()):
    person_list = person_list.distinct()  # ensure persons are only in the list once
    doblist = []
    doblist.extend(list(person_list.filter(
        date_of_birth__month=from_date.month, date_of_birth__day=from_date.day)))
    next_day = from_date + datetime.timedelta(days=1)
    for day in range(0, days):
        doblist.extend(list(person_list.filter(
            date_of_birth__month=next_day.month, date_of_birth__day=next_day.day, date_of_death__isnull=True)))
        next_day = next_day + datetime.timedelta(days=1)
    for dob in doblist:
        dob.date_of_birth = dob.date_of_birth.replace(
            year=get_today().year)
    return doblist


def get_coming_sunday(date=get_today()):
    # coming sunday's date
    coming_sunday = date
    while coming_sunday.weekday() != 6:
        coming_sunday += datetime.timedelta(1)
    return coming_sunday


def ahead_or_behind(collection, goal):
    if collection > goal:
        return "ahead"
    elif collection < goal:
        return "behind"


def is_contributor(user):
    return user.groups.filter(name='contributor').exists()


def is_editor(user):
    return user.groups.filter(name='editor').exists()


def is_bulletin_approver(user):
    return user.groups.filter(name='bulletin_approver').exists()


def template_email(template_name, extra_context=None, *args, **kwargs):
    """
    Thanks to https://gist.github.com/SmileyChris/5881290

    Return an :cls:`~django.core.mail.EmailMessage` with the body (and
    optionally, the subject) set from django templates.
    :param template_name: The template name, or partial template name.
    :param extra_context: A dictionary of context data to pass to the email
        templates.
    Passing the full template name will render the email body using this
    template. If the template extension is ``htm`` or ``html``, the message
    mime subtype will be changed to ``html``. For example::
        message = template_email(
            template_name='emails/alert.txt', subject="Alert!",
            to=['bob@example.com'])
        message.send()
    Passing a partial template allows a plain text body, an HTML alternative,
    and the subject to all be templates. For example, calling
    ``template_email(template_name='emails/welcome')`` will look for the
    following templates:
    * ``emails/welcome_subject.txt`` will set the message's subject line. Only
      the first non-blank line of this file will be used.
    * ``emails/welcome.txt`` will be the plain text body.
    * ``emails/welcome.html`` will be the HTML alternative if a plain text body
      is also found, otherwise it'll be the body and the message mime subtype
      will be changed to ``html``.
    If neither the plain text or HTML template exist, a
    :cls:`~django.template.TemplateDoesNotExist` exception will be raised. The
    subject template is optional.
    The subject and plain text body templates are rendered with auto-escape
    turned off.
    """
    message = mail.EmailMultiAlternatives(*args, **kwargs)

    context = template.Context(extra_context)

    html_template_names = ['{}.html'.format(template_name)]
    txt_template_names = ['{}.txt'.format(template_name)]
    if os.path.splitext(template_name)[1].lower() in ('.htm', '.html'):
        html_template_names.append(template_name)
    else:
        txt_template_names.append(template_name)

    # Get the HTML body.
    try:
        html = select_template(html_template_names).render(context)
    except template.TemplateDoesNotExist:
        html = None

    print(html)

    # The remainder of the templates are text only, so turn off autoescaping.
    context.autoescape = False

    # Get the plain-text body.
    try:
        txt = select_template(txt_template_names).render(context)
    except template.TemplateDoesNotExist:
        if not html:
            # Neither body template exists.
            raise
        txt = None

    # Get the subject.
    try:
        subject = (
            get_template('{}_subject.txt'.format(template_name))
            .render(context)
        )
        message.subject = subject.strip().splitlines()[0]
    except template.TemplateDoesNotExist:
        pass

    if txt:
        message.body = txt
        if html:
            message.attach_alternative(html, 'text/html')
    else:
        message.content_subtype = 'html'
        message.body = html

    return message


def send_bulletin(request):

    message = template_email(
        template_name='emails/bulletin',
        subject='GBM Bulletin',
        to=['yannhowe@gmail.com']
    )
    message.send()
    messages.add_message(request, messages.INFO,
                         'Bulletin emailed to you.')
    return HttpResponseRedirect(reverse('home'))


class BulletinContextMixin(ContextMixin):

    def get_context_data(self, **kwargs):
        context = super(BulletinContextMixin, self).get_context_data(**kwargs)

        order_of_service = None
        coming_sunday_order_of_service = None

        context['is_bulletin_approver'] = is_bulletin_approver(self.request.user)
        context['is_editor'] = is_editor(self.request.user)
        context['is_contributor'] = is_contributor(self.request.user)

        try:
            order_of_service = OrderOfService.objects.all()
        except OrderOfService.DoesNotExist:
            order_of_service = None
            coming_sunday_order_of_service = None

        if order_of_service:
            try:
                coming_sunday_order_of_service = order_of_service.order_by('date').filter(date=get_coming_sunday(get_today()))[:1].get()
            except OrderOfService.DoesNotExist:
                coming_sunday_order_of_service = None

        if coming_sunday_order_of_service is not None:
            context['coming_sunday_order_of_service'] = coming_sunday_order_of_service
            context['orderofservice_updated_or_not'] = True if get_coming_sunday(get_today()).strftime('%b. %d, %Y') == coming_sunday_order_of_service.date.strftime('%b. %d, %Y') else False

        try:
            announcements = Announcement.objects.all()
        except Announcement.DoesNotExist:
            announcements = None

        if announcements:
            announcements_under_review = announcements.filter(publish_end_date__gte=get_now(), under_review=True)
            announcements_under_review_count = announcements_under_review.count()

            context['all_announcements'] = announcements
            context['announcements_under_review'] = announcements_under_review
            context['announcements_under_review_count'] = announcements_under_review_count

            published_announcements = announcements.filter(publish_start_date__lte=get_now(), publish_end_date__gte=get_now()).filter(hidden=False, under_review=False).extra(order_by=['-publish_start_date', 'publish_end_date'])
            published_announcements_print = announcements.filter(publish_start_date__lte=get_coming_sunday(get_today()), publish_end_date__gte=get_coming_sunday(get_today())).filter(hidden=False, under_review=False).extra(order_by=['-publish_start_date', 'publish_end_date'])

            if published_announcements is not None:
                context['published_announcements'] = published_announcements
                max_print_annoucements = int(config.MAX_PRINT_ANNOUCEMENTS)
                context['announcements_print'] = published_announcements_print[:max_print_annoucements]
                context['more_annoucements_online_count'] = published_announcements.count() - max_print_annoucements

        try:
            sunday_attendance = SundayAttendance.objects.all()
        except SundayAttendance.DoesNotExist:
            sunday_attendance = None

        if sunday_attendance:
            sunday_attendance_under_review = sunday_attendance.filter(under_review=True)
            sunday_attendance_under_review_count = sunday_attendance_under_review.count()
            context['sunday_attendance_under_review'] = sunday_attendance_under_review
            context['graph_sunday_attendance'] = sunday_attendance.order_by('-date')[:25]
            context['recent_sunday_attendance'] = sunday_attendance.order_by(
                '-date')[:4]
            context[
                'sunday_attendance_under_review_count'] = sunday_attendance_under_review_count

        if sunday_attendance and announcements:
            context['total_under_review_count'] = announcements_under_review_count + \
                sunday_attendance_under_review_count

        context['theme'] = {'this_year_theme': config.THIS_YEAR_THEME,
                            'this_year_theme_verse': config.THIS_YEAR_THEME_VERSE,
                            'this_year_theme_year': config.THIS_YEAR_THEME_YEAR}

        try:
            all_birthdays = Profile.objects.exclude(date_of_birth=None)
        except Profile.DoesNotExist:
            all_birthdays = None

        if all_birthdays is not None:
            context['birthdays'] = get_upcoming_birthdays(all_birthdays, 6)
            context['birthdays_after_coming_sunday'] = get_upcoming_birthdays(
                all_birthdays, 6, get_coming_sunday(get_today()))

        SundayAttendanceApproved = SundayAttendance.objects.exclude(under_review=True)
        context['graph_sunday_attendance'] = SundayAttendanceApproved.order_by('-date')[:25]
        context['recent_sunday_attendance'] = SundayAttendanceApproved.order_by('-date')[:4]
        context['latest_sunday_attendance'] = SundayAttendanceApproved.order_by('-date')[:1]

        try:
            latest_weeklyverse = WeeklyVerse.objects.latest('date')
        except WeeklyVerse.DoesNotExist:
            latest_weeklyverse = None

        if latest_weeklyverse is not None:
            context['weeklyverse'] = latest_weeklyverse
            context['weeklyverse_updated_or_not'] = True if get_coming_sunday(get_today()).strftime('%b. %d, %Y') == latest_weeklyverse.date.strftime('%b. %d, %Y') else False

        try:
            active_events = Event.objects.filter(Q(date_end__gte=get_now()) | Q(date_start__gte=get_now()))
        except Event.DoesNotExist:
            active_events = None

        context['events'] = active_events.exclude(date_start__lt=get_now()).exclude(Q(date_end__gt=get_future(60)) & ~Q(display_override__iexact='SHOW')).exclude(Q(display_override__iexact='HIDE')).extra(order_by=['date_start'])[:20]
        context['events_in_future_all'] = active_events.exclude(date_end__lt=get_now()).exclude(Q(display_override__iexact='HIDE')).extra(order_by=['date_start'])
        context['events_print'] = active_events.exclude(date_start__lt=get_coming_sunday()).exclude(Q(date_end__gt=get_future(60)) & ~Q(display_override__iexact='SHOW')).exclude(Q(display_override__iexact='HIDE')).extra(order_by=['date_start'])[:7]

        context['now'] = get_now()
        context['today'] = get_today()
        context['coming_sunday'] = get_coming_sunday()

        try:
            building_fund_collection = BuildingFundCollection.objects.filter(date__year=get_now().year)
        except BuildingFundCollection.DoesNotExist:
            building_fund_collection = None

        try:
            building_fund_year_goal = BuildingFundYearGoal.objects.filter(date__year=get_now().year)
        except BuildingFundYearGoal.DoesNotExist:
            building_fund_year_goal = None

        try:
            building_fund_year_pledge = BuildingFundYearPledge.objects.filter(date__year=get_now().year)
        except BuildingFundYearPledge.DoesNotExist:
            building_fund_year_pledge = None

        if building_fund_collection:
            building_fund_collection_ytd = list(building_fund_collection.filter(date__year=get_now().year).aggregate(Sum('amount')).values())[0]

            context['building_fund_collection_latest'] = building_fund_collection.latest('date')
            context['building_fund_collection_ytd'] = building_fund_collection_ytd

            if building_fund_year_goal:
                building_fund_year_goal = building_fund_year_goal.latest('date').amount
                building_goal_and_ytd_collection_difference = building_fund_year_goal - building_fund_collection_ytd
                building_goal_and_ytd_collection_percent = building_fund_collection_ytd / building_fund_year_goal * 100
                ahead_or_behind_goal = ahead_or_behind(building_fund_collection_ytd, building_fund_year_goal)

                context['building_fund_year_goal'] = building_fund_year_goal
                context['building_goal_and_ytd_collection_difference'] = abs(building_goal_and_ytd_collection_difference)
                context['building_goal_and_ytd_collection_percent'] = building_goal_and_ytd_collection_percent
                context['ahead_or_behind'] = ahead_or_behind_goal

                if building_fund_year_pledge:
                    building_fund_pledged_ytd = building_fund_year_pledge.latest('date').amount / 365 * get_now().timetuple().tm_yday
                    building_pledge_and_ytd_collection_difference = building_fund_pledged_ytd - building_fund_collection_ytd

                    context['building_fund_pledged_ytd'] = building_fund_pledged_ytd
                    context['building_pledge_and_ytd_collection_difference'] = abs(building_pledge_and_ytd_collection_difference)

        if self.request.user.is_authenticated:
            try:
                signup_list = Signup.objects.filter(
                    event__in=active_events).filter(user=self.request.user)
            except Signup.DoesNotExist:
                signup_list = None
            context['signups'] = signup_list.all()

        if self.request.user.is_authenticated:
            try:
                signup_id_list = Signup.objects.filter(
                    event__in=active_events).filter(user=self.request.user).values_list('event_id', flat=True)
            except Signup.DoesNotExist:
                signup_id_list = None
            context['signup_id_list'] = signup_id_list.all()

        context['categories'] = Category.objects.all()
        return context


class NeedsReviewMixin(object):

    def form_valid(self, form):
        submission = form.save(commit=False)
        submission.submitter = User.objects.get(
            username=self.request.user)
        submission.approver = None
        submission.under_review = True
        submission.save()
        # TODO Email admins that new announcement has been submitted for review
        message = template_email(
            template_name='emails/new_item_for_review',
            to=config.UNDER_REVIEW_ADMINS.split()
        )
        message.send()
        return HttpResponseRedirect(self.success_url)


class RecordSubmitterMixin(object):

    def form_valid(self, form):
        submission = form.save(commit=False)
        submission.submitter = User.objects.get(
            username=self.request.user)
        submission.save()
        return HttpResponseRedirect(self.success_url)


class LoginRequiredMixin(object):
    # mixin from https://gist.github.com/robgolding/3092600
    """
    View mixin which requires that the user is authenticated.
    """
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(self, request, *args, **kwargs)


class ContributorRequiredMixin(object):
    # mixin from https://gist.github.com/robgolding/3092600

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not is_contributor(request.user):
            messages.error(
                request,
                'You do not have the permission required to perform the '
                'requested operation.')
            return redirect(settings.LOGIN_URL)
        return super(ContributorRequiredMixin, self).dispatch(request, *args, **kwargs)


class EditorRequiredMixin(object):
    # mixin from https://gist.github.com/robgolding/3092600

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not is_editor(request.user):
            messages.error(
                request,
                'You do not have the permission required to perform the '
                'requested operation.')
            return redirect(settings.LOGIN_URL)
        return super(EditorRequiredMixin, self).dispatch(request, *args, **kwargs)


class BulletinApproverRequiredMixin(object):
    # mixin from https://gist.github.com/robgolding/3092600

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not is_bulletin_approver(request.user):
            messages.error(
                request,
                'You do not have the permission required to perform the '
                'requested operation.')
            return redirect(settings.LOGIN_URL)
        return super(BulletinApproverRequiredMixin, self).dispatch(request, *args, **kwargs)


class SuperUserRequiredMixin(object):
    # mixin from https://gist.github.com/robgolding/3092600
    """
    View mixin which requires that the authenticated user is a super user
    (i.e. `is_superuser` is True).
    """
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            messages.error(
                request,
                'You do not have the permission required to perform the '
                'requested operation.')
            return redirect(settings.LOGIN_URL)
        return super(SuperUserRequiredMixin, self).dispatch(request,
                                                            *args, **kwargs)


class PdfResponseMixin(object, ):

    def render_to_response(self, context, **response_kwargs):
        context = self.get_context_data()
        template = self.get_template_names()[0]
        html_string = render_to_string(template, context)
        rendered_html = HTML(string=html_string)
        pdf_file = rendered_html.write_pdf()
        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = 'filename="mypdf.pdf"'
        return response


class UnderReviewListView(EditorRequiredMixin, ListView):
    model = Announcement
    template_name = 'newswire/cp/under_review_list.html'

    def get_context_data(self, **kwargs):
        context = super(UnderReviewListView, self).get_context_data(**kwargs)

        try:
            announcements = Announcement.objects.all()
        except Announcement.DoesNotExist:
            announcements = None

        if announcements:
            announcements_under_review = announcements.filter(publish_end_date__gte=get_now(), under_review=True)
            announcements_under_review_count = announcements_under_review.count()
            context['announcements_under_review'] = announcements_under_review
            context['announcements_under_review_count'] = announcements_under_review_count

        try:
            sunday_attendance = SundayAttendance.objects.all()
        except SundayAttendance.DoesNotExist:
            sunday_attendance = None

        if sunday_attendance:
            sunday_attendance_under_review = sunday_attendance.filter(under_review=True)
            sunday_attendance_under_review_count = sunday_attendance_under_review.count()
            context['sunday_attendance_under_review'] = sunday_attendance_under_review
            context['graph_sunday_attendance'] = sunday_attendance.order_by('-date')[:25]
            context['recent_sunday_attendance'] = sunday_attendance.order_by('-date')[:4]
            context['sunday_attendance_under_review_count'] = sunday_attendance_under_review_count

        if sunday_attendance and announcements:
            context['total_under_review_count'] = announcements_under_review_count + sunday_attendance_under_review_count

        return context


class BulletinListView(ListView, BulletinContextMixin):
    model = Announcement
    template_name = 'newswire/home.html'

    def get_queryset(self):
        # do not show archived instances.
        qs = super(ListView, self).get_queryset()
        return qs


class BulletinHomePageView(BulletinListView):
    template_name = 'newswire/home.html'


class BulletinPrintView(EditorRequiredMixin, BulletinListView):
    template_name = 'newswire/cp/bulletin_print.html'


class BulletinPdfView(EditorRequiredMixin, PdfResponseMixin, BulletinListView):
    template_name = 'newswire/cp/bulletin_pdf.html'

    def render_to_response(self, context, **response_kwargs):
        context = self.get_context_data()
        template = self.get_template_names()[0]
        html_string = render_to_string(template, context)
        rendered_html = HTML(string=html_string)
        pdf_file = rendered_html.write_pdf(stylesheets=[CSS(settings.BASE_DIR + '/newswire/static/newswire/cp/css/bootstrap.min.css'), CSS(settings.BASE_DIR + '/newswire/static/newswire/cp/css/font-awesome.min.css'), CSS(settings.BASE_DIR + '/newswire/static/newswire/cp/css/gbm_bulletin_pdf.css')])
        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = 'filename="mypdf.pdf"'
        return response


class BulletinPdfPreviewView(EditorRequiredMixin, BulletinListView):
    template_name = 'newswire/cp/bulletin_preview.html'


class BulletinPdfSendView(BulletinApproverRequiredMixin, TemplateView, BulletinContextMixin):
    template_name = 'newswire/cp/bulletin_pdf.html'

    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            context = self.get_context_data()
            template = self.get_template_names()[0]
            html_string = render_to_string(template, context)
            rendered_html = HTML(string=html_string)
            filename = get_coming_sunday(get_today()).strftime('%Y%m%d') + '_gbm_bulletin.pdf'
            pdf_file = rendered_html.write_pdf(stylesheets=[CSS(settings.BASE_DIR + '/newswire/static/newswire/cp/css/bootstrap.min.css'), CSS(settings.BASE_DIR + '/newswire/static/newswire/cp/css/font-awesome.min.css'), CSS(settings.BASE_DIR + '/newswire/static/newswire/cp/css/gbm_bulletin_pdf.css')])

            if self.request.user.profile.first_name or self.request.user.profile.last_name:
                approver_name = self.request.user.profile.first_name + ', ' + self.request.user.profile.last_name
            else:
                approver_name = 'an admin'

            recipients = config.BULLETIN_PRINT_ADMIN_LIST.split()
            if self.request.user.profile.email:
                recipients.append(self.request.user.profile.email)

            email = EmailMessage(
                'GBM Bulletin: Bulletin for %s is ready for print' % (get_coming_sunday(get_today()).strftime('%b. %d, %Y')),
                'Attached is the bulletin approved by %s for print' % (approver_name),
                'bulletin@gbm.sg',
                recipients,
                [''],
                reply_to=['bulletin@gbm.sg'],
            )
            email.attach(filename, pdf_file)
            email.send(fail_silently=False)
        return HttpResponseRedirect(reverse('cp_bulletin_pdf_preview'))

    def get_queryset(self):
        # do not show archived instances.
        qs = super(ListView, self).get_queryset()
        return qs


class OrderOfServiceList(EditorRequiredMixin, ListView):
    model = OrderOfService
    queryset = OrderOfService.objects.order_by('-date')
    template_name = 'newswire/cp/orderofservice_list.html'
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super(OrderOfServiceList, self).get_context_data(**kwargs)

        liveorderofservice = None
        try:
            liveorderofservice = OrderOfService.objects.order_by('date').filter(
                date__gte=get_now())[:1].get()
        except OrderOfService.DoesNotExist:
            liveorderofservice = None
        context['live_orderofservice'] = liveorderofservice
        context['orderofservice'] = OrderOfService.objects.order_by('-date')
        context['highlight'] = {
            'oos_tip_lines': config.ORDER_OF_SERVICE_TIP_LINES,
            'oos_warning_lines': config.ORDER_OF_SERVICE_WARNING_LINES,
        }

        return context

    def get_queryset(self):
        # do not show archived instances.
        qs = super(ListView, self).get_queryset()
        return qs


class OrderOfServiceCreate(EditorRequiredMixin, CreateView):
    model = OrderOfService
    success_url = reverse_lazy('orderofservice_list')
    form_class = OrderOfServiceForm
    template_name = 'newswire/cp/orderofservice_form.html'


class OrderOfServiceUpdate(EditorRequiredMixin, UpdateView):
    model = OrderOfService
    success_url = reverse_lazy('orderofservice_list')
    form_class = OrderOfServiceForm
    template_name = 'newswire/cp/orderofservice_form.html'


class OrderOfServiceDelete(EditorRequiredMixin, DeleteView):
    model = OrderOfService
    success_url = reverse_lazy('orderofservice_list')
    template_name = 'newswire/cp/orderofservice_confirm_delete.html'


class AnnouncementList(EditorRequiredMixin, ListView):
    queryset = Announcement.objects.order_by('-publish_end_date', '-publish_start_date')
    template_name = 'newswire/cp/announcement_list.html'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super(AnnouncementList, self).get_context_data(**kwargs)

        try:
            categories = Category.objects.all()
        except Category.DoesNotExist:
            categories = None
        context['categories'] = categories

        try:
            announcements = Announcement.objects.all()
        except Announcement.DoesNotExist:
            announcements = None

        if announcements:
            context['all_announcements'] = announcements
            all_announcements_sorted = announcements.extra(order_by=['-publish_end_date', '-publish_start_date'])
            context['all_announcements_sorted'] = all_announcements_sorted

        return context


class AnnouncementCreate(EditorRequiredMixin, RecordSubmitterMixin, CreateView):
    model = Announcement
    success_url = reverse_lazy('announcement_list')
    form_class = AnnouncementForm
    template_name = 'newswire/cp/announcement_form.html'


class AnnouncementUpdate(EditorRequiredMixin, RecordSubmitterMixin, UpdateView):
    model = Announcement
    success_url = reverse_lazy('announcement_list')
    form_class = AnnouncementForm
    template_name = 'newswire/cp/announcement_form.html'


class UnderReviewFrontEndListView(ContributorRequiredMixin, ListView):
    model = Announcement
    template_name = 'newswire/submissions_under_review.html'

    def get_context_data(self, **kwargs):
        context = super(UnderReviewFrontEndListView,
                        self).get_context_data(**kwargs)

        try:
            announcements = Announcement.objects.filter(
                submitter=self.request.user, publish_end_date__gte=get_today() - datetime.timedelta(days=28))
        except Announcement.DoesNotExist:
            announcements = None

        if announcements:
            announcements_under_review = announcements.filter(under_review=True)
            announcements_approved = announcements.filter(under_review=False)
            context['announcements_under_review'] = announcements_under_review
            context['announcements_approved'] = announcements_approved

        try:
            sunday_attendance = SundayAttendance.objects.filter(
                submitter=self.request.user, date__gte=get_today() - datetime.timedelta(days=28))
        except SundayAttendance.DoesNotExist:
            sunday_attendance = None

        if sunday_attendance:
            sunday_attendance_under_review = sunday_attendance.filter(
                under_review=True)
            sunday_attendance_approved = sunday_attendance.filter(
                under_review=False)
            context['sunday_attendance_under_review'] = sunday_attendance_under_review
            context['sunday_attendance_approved'] = sunday_attendance_approved

        return context


class AnnouncementFrontEndCreate(ContributorRequiredMixin, NeedsReviewMixin, CreateView):
    model = Announcement
    success_url = reverse_lazy('under_review_front_end')
    form_class = AnnouncementFormFrontEnd
    template_name = 'newswire/update-form.html'
    page = Context({
        'title': 'Create Announcement - ',
        'header': 'Announcement Review Form',
        'description': 'Use this to submit announcements for review'
    })

    def get_context_data(self, **kwargs):
        context = super(AnnouncementFrontEndCreate,
                        self).get_context_data(**kwargs)
        context['page'] = self.page
        return context


class AnnouncementFrontEndUpdate(ContributorRequiredMixin, NeedsReviewMixin, UpdateView):
    model = Announcement
    success_url = reverse_lazy('under_review_front_end')
    form_class = AnnouncementFormFrontEnd
    template_name = 'newswire/update-form.html'
    page = Context({
        'title': 'Update Sunday Announcement - ',
        'header': 'Update Sunday Announcement',
        'description': 'Use this to update announcements'
    })

    def get_context_data(self, **kwargs):
        context = super(AnnouncementFrontEndUpdate,
                        self).get_context_data(**kwargs)
        context['page'] = self.page
        return context


class AnnouncementFrontEndDelete(ContributorRequiredMixin, DeleteView):
    model = Announcement
    success_url = reverse_lazy('under_review_front_end')
    template_name = 'newswire/delete-form.html'
    page = Context({
        'title': 'Delete Sunday Announcement - ',
        'header': 'Delete Sunday Announcement',
        'description': 'Use this to delete announcements'
    })

    def get_context_data(self, **kwargs):
        context = super(AnnouncementFrontEndDelete,
                        self).get_context_data(**kwargs)
        context['page'] = self.page
        return context


class AnnouncementDelete(EditorRequiredMixin, DeleteView):
    model = Announcement
    success_url = reverse_lazy('announcement_list')
    template_name = 'newswire/cp/announcement_confirm_delete.html'


class UnderReviewApproveView(EditorRequiredMixin, DetailView):

    def post(self, request, *args, **kwargs):
        if request.method == 'POST':

            the_user = request.user
            response_data = {}
            announcenment = Announcement()

            approval_object_id = request.POST.get('approval_object_id')
            approval_object_type = request.POST.get('approval_object_type')
            something_updated_successfully = False

            if approval_object_type == "announcement":
                try:
                    announcenment = Announcement()
                    announcenment = Announcement.objects.get(
                        pk=approval_object_id)
                    announcenment.under_review = False
                    announcenment.approver = the_user
                    announcenment.save()
                    something_updated_successfully = True
                except:
                    pass

            if approval_object_type == "attendance":
                try:
                    attendance = SundayAttendance()
                    attendance = SundayAttendance.objects.get(
                        pk=approval_object_id)
                    attendance.under_review = False
                    attendance.approver = the_user
                    attendance.save()
                    something_updated_successfully = True
                except:
                    pass

            if something_updated_successfully:
                response_data['approval_object_status'] = "Updated"
                return HttpResponse(
                    json.dumps(response_data),
                    content_type="application/json"
                )
            else:
                response_data['approval_object_status'] = "Update Failed"
                return HttpResponse(
                    json.dumps(response_data),
                    content_type="application/json"
                )

        else:
            return HttpResponse(
                json.dumps({"nothing to see": "this isn't happening"}),
                content_type="application/json"
            )

    def get_success_url(self):
        return reverse('home')

    def get_object(self):
        return get_object_or_404(User, pk=self.request.user.id)


class EventList(EditorRequiredMixin, ListView):
    queryset = Event.objects.order_by('-date_start')
    template_name = 'newswire/cp/event_list.html'


class EventCreate(EditorRequiredMixin, CreateView):
    model = Event
    success_url = reverse_lazy('event_list')
    form_class = EventForm
    template_name = 'newswire/cp/event_form.html'


class EventUpdate(EditorRequiredMixin, UpdateView):
    model = Event
    success_url = reverse_lazy('event_list')
    form_class = EventForm
    template_name = 'newswire/cp/event_form.html'


class EventDelete(EditorRequiredMixin, DeleteView):
    model = Event
    success_url = reverse_lazy('event_list')
    template_name = 'newswire/cp/event_confirm_delete.html'


class EventListFrontEndView(ListView):
    model = Event
    template_name = 'newswire/event-list.html'

    def get_context_data(self, **kwargs):
        context = super(EventListFrontEndView,
                        self).get_context_data(**kwargs)
        try:
            active_events = Event.objects.filter(Q(date_end__gte=get_now()) | Q(date_start__gte=get_now()))
        except Event.DoesNotExist:
            active_events = None

        if active_events:
            context['events_in_future_all'] = active_events.exclude(date_end__lt=get_now()).exclude(Q(display_override__iexact='HIDE')).extra(order_by=['date_start'])
        return context


class CategoryList(EditorRequiredMixin, ListView):
    queryset = Category.objects.all()
    template_name = 'newswire/cp/category_list.html'


class CategoryCreate(EditorRequiredMixin, CreateView):
    model = Category
    success_url = reverse_lazy('announcement_list')
    form_class = CategoryForm
    template_name = 'newswire/cp/category_form.html'


class CategoryUpdate(EditorRequiredMixin, UpdateView):
    model = Category
    success_url = reverse_lazy('announcement_list')
    form_class = CategoryForm
    template_name = 'newswire/cp/category_form.html'


class CategoryDelete(EditorRequiredMixin, DeleteView):
    model = Category
    success_url = reverse_lazy('announcement_list')
    template_name = 'newswire/cp/category_confirm_delete.html'


class ProfileSummary(EditorRequiredMixin, ListView):
    queryset = Profile.objects.all()
    template_name = 'newswire/cp/profile_summary.html'

    def get_context_data(self, **kwargs):
        context = super(ProfileSummary, self).get_context_data(**kwargs)

        try:
            all_profiles = Profile.objects.all()
        except Profile.DoesNotExist:
            all_profiles = none

        context['all_profiles'] = all_profiles
        context['members'] = all_profiles.filter(is_member=True)
        context['non_members'] = all_profiles.filter(is_member=False)
        context['regular_non_members'] = all_profiles.filter(is_regular=True, is_member=False)
        context['non_regular_members'] = all_profiles.filter(is_regular=False, is_member=True)

        return context


class ProfileList(EditorRequiredMixin, ListView):
    queryset = Profile.objects.all()
    template_name = 'newswire/cp/profile_list.html'


class ProfileCreate(EditorRequiredMixin, CreateView):
    model = Profile
    success_url = reverse_lazy('profile_list')
    form_class = ProfileForm
    template_name = 'newswire/cp/profile_form.html'


class ProfileUpdate(EditorRequiredMixin, UpdateView):
    model = Profile
    success_url = reverse_lazy('profile_list')
    form_class = ProfileForm
    template_name = 'newswire/cp/profile_form.html'


class ProfileDelete(EditorRequiredMixin, DeleteView):
    model = Profile
    success_url = reverse_lazy('profile_list')
    template_name = 'newswire/cp/profile_confirm_delete.html'


class ProfileDetailFrontEndView(DetailView):
    template_name = 'newswire/profile-detail.html'

    def get_context_data(self, **kwargs):
        context = super(ProfileDetailFrontEndView,
                        self).get_context_data(**kwargs)
        context['user'] = self.request.user
        context['profile'] = self.request.user.profile
        return context

    def get_object(self):
        return get_object_or_404(User, pk=self.request.user.id)


class ProfileUpdateFrontEndView(UpdateView):
    model = Profile
    form_class = ProfileFrontEndForm
    template_name = 'newswire/profile-update.html'

    def get_success_url(self):
        return reverse('profile_front_end_detail')

    def get_object(self):
        return Profile.objects.get(user=self.request.user)


class AttendanceSummary(EditorRequiredMixin, ListView):
    queryset = SundayAttendance.objects.all()
    template_name = 'newswire/cp/attendance_summary.html'

    def get_context_data(self, **kwargs):
        context = super(AttendanceSummary, self).get_context_data(**kwargs)
        context['graph_sunday_attendance'] = SundayAttendance.objects.order_by(
            '-date')[:25]
        context['recent_sunday_attendance'] = SundayAttendance.objects.order_by(
            '-date')[:4]
        return context


class AttendanceCreate(EditorRequiredMixin, RecordSubmitterMixin, CreateView):
    model = SundayAttendance
    success_url = reverse_lazy('attendance_new')
    form_class = AttendanceForm
    template_name = 'newswire/cp/attendance_form.html'


class AttendanceUpdate(EditorRequiredMixin, RecordSubmitterMixin, UpdateView):
    model = SundayAttendance
    success_url = reverse_lazy('attendance_summary')
    form_class = AttendanceForm
    template_name = 'newswire/cp/attendance_form.html'


class AttendanceDelete(EditorRequiredMixin, DeleteView):
    model = SundayAttendance
    success_url = reverse_lazy('attendance_summary')
    template_name = 'newswire/cp/attendance_confirm_delete.html'


class AttendanceFrontEndCreate(ContributorRequiredMixin, NeedsReviewMixin, CreateView):
    model = SundayAttendance
    success_url = reverse_lazy('under_review_front_end')
    form_class = AttendanceFormFrontEnd
    template_name = 'newswire/update-form.html'
    page = Context({
        'title': 'Create Sunday Attendance - ',
        'header': 'Sunday Attendance Form',
        'description': 'Use this to submit attendance records for review'
    })

    def get_context_data(self, **kwargs):
        context = super(AttendanceFrontEndCreate,
                        self).get_context_data(**kwargs)
        context['page'] = self.page
        return context


class AttendanceFrontEndUpdate(ContributorRequiredMixin, NeedsReviewMixin, UpdateView):
    model = SundayAttendance
    success_url = reverse_lazy('under_review_front_end')
    form_class = AttendanceFormFrontEnd
    template_name = 'newswire/update-form.html'
    page = Context({
        'title': 'Update Sunday Attendance - ',
        'header': 'Update Sunday Attendance',
        'description': 'Use this to update attendance records'
    })


class AttendanceFrontEndDelete(ContributorRequiredMixin, DeleteView):
    model = SundayAttendance
    success_url = reverse_lazy('under_review_front_end')
    template_name = 'newswire/delete-form.html'
    page = Context({
        'title': 'Delete Sunday Attendance - ',
        'header': 'Delete Sunday Attendance',
        'description': 'Use this to delete attendance records'
    })


class WeeklyVerseList(EditorRequiredMixin, ListView):
    queryset = WeeklyVerse.objects.order_by('-date')
    template_name = 'newswire/cp/weeklyverse_list.html'
    paginate_by = 3


class WeeklyVerseCreate(EditorRequiredMixin, CreateView):
    model = WeeklyVerse
    success_url = reverse_lazy('weeklyverse_list')
    form_class = WeeklyVerseForm
    template_name = 'newswire/cp/weeklyverse_form.html'


class WeeklyVerseUpdate(EditorRequiredMixin, UpdateView):
    model = WeeklyVerse
    success_url = reverse_lazy('weeklyverse_list')
    form_class = WeeklyVerseForm
    template_name = 'newswire/cp/weeklyverse_form.html'


class WeeklyVerseDelete(EditorRequiredMixin, DeleteView):
    model = WeeklyVerse
    success_url = reverse_lazy('weeklyverse_list')
    template_name = 'newswire/cp/weeklyverse_confirm_delete.html'


class BuildingFundList(EditorRequiredMixin, ListView):
    model = BuildingFundCollection
    template_name = 'newswire/cp/buildingfund.html'

    def get_context_data(self, **kwargs):
        context = super(BuildingFundList, self).get_context_data(**kwargs)

        try:
            building_fund_collection = BuildingFundCollection.objects.all()
            context['building_fund_collection'] = building_fund_collection
            context['latest_building_fund_collection'] = BuildingFundCollection.objects.latest(
                'date')
        except BuildingFundCollection.DoesNotExist:
            building_fund_collection = None

        try:
            building_fund_year_pledge = BuildingFundYearPledge.objects.all()
            context['building_fund_year_pledge'] = building_fund_year_pledge
            context['latest_building_fund_year_pledge'] = BuildingFundYearPledge.objects.latest(
                'date')
        except BuildingFundYearPledge.DoesNotExist:
            building_fund_year_pledge = None

        try:
            building_fund_year_goal = BuildingFundYearGoal.objects.all()
            context['building_fund_year_goal'] = building_fund_year_goal
            context['latest_building_fund_year_goal'] = BuildingFundYearGoal.objects.latest(
                'date')
        except BuildingFundYearGoal.DoesNotExist:
            building_fund_year_goal = None

        return context


class BuildingFundCollectionCreate(EditorRequiredMixin, CreateView):
    model = BuildingFundCollection
    success_url = reverse_lazy('buildingfund_list')
    form_class = BuildingFundCollectionForm
    template_name = 'newswire/cp/buildingfundcollection_form.html'


class BuildingFundCollectionUpdate(EditorRequiredMixin, UpdateView):
    model = BuildingFundCollection
    success_url = reverse_lazy('buildingfund_list')
    form_class = BuildingFundCollectionForm
    template_name = 'newswire/cp/buildingfundcollection_form.html'


class BuildingFundCollectionDelete(EditorRequiredMixin, DeleteView):
    model = BuildingFundCollection
    success_url = reverse_lazy('buildingfund_list')
    template_name = 'newswire/cp/buildingfundcollection_confirm_delete.html'


class BuildingFundYearPledgeCreate(EditorRequiredMixin, CreateView):
    model = BuildingFundYearPledge
    success_url = reverse_lazy('buildingfund_list')
    form_class = BuildingFundYearPledgeForm
    template_name = 'newswire/cp/buildingfundyearpledge_form.html'


class BuildingFundYearPledgeUpdate(EditorRequiredMixin, UpdateView):
    model = BuildingFundYearPledge
    success_url = reverse_lazy('buildingfund_list')
    form_class = BuildingFundYearPledgeForm
    template_name = 'newswire/cp/buildingfundyearpledge_form.html'


class BuildingFundYearPledgeDelete(EditorRequiredMixin, DeleteView):
    model = BuildingFundYearPledge
    success_url = reverse_lazy('buildingfund_list')
    template_name = 'newswire/cp/buildingfundyearpledge_confirm_delete.html'


class BuildingFundYearGoalCreate(EditorRequiredMixin, CreateView):
    model = BuildingFundYearGoal
    success_url = reverse_lazy('buildingfund_list')
    form_class = BuildingFundYearGoalForm
    template_name = 'newswire/cp/buildingfundyeargoal_form.html'


class BuildingFundYearGoalUpdate(EditorRequiredMixin, UpdateView):
    model = BuildingFundYearGoal
    success_url = reverse_lazy('buildingfund_list')
    form_class = BuildingFundYearGoalForm
    template_name = 'newswire/cp/buildingfundyeargoal_form.html'


class BuildingFundYearGoalDelete(EditorRequiredMixin, DeleteView):
    model = BuildingFundYearGoal
    success_url = reverse_lazy('buildingfund_list')
    template_name = 'newswire/cp/buildingfundyeargoal_confirm_delete.html'


class RsvpUpdateView(DetailView):

    model = Signup

    def post(self, request, *args, **kwargs):
        if request.method == 'POST':

            the_user = request.user
            the_rsvp = request.POST.get('the_rsvp')
            the_event = Event.objects.get(pk=request.POST.get('the_event'))
            the_pk = ""
            response_data = {}
            signup = Signup()

            try:
                the_pk = Signup.objects.get(event=the_event, user=the_user).pk
                signup.pk = the_pk
            except:
                pass

            signup.user = the_user
            signup.event = the_event
            signup.rsvp = the_rsvp
            signup.save()

            response_data['the_rsvp'] = signup.rsvp
            response_data['the_event'] = signup.event.pk

            if the_pk:
                response_data['record'] = "updated"
                return HttpResponse(
                    json.dumps(response_data),
                    content_type="application/json"
                )
            else:
                response_data['record'] = "created"
                return HttpResponse(
                    json.dumps(response_data),
                    content_type="application/json"
                )

        else:
            return HttpResponse(
                json.dumps({"nothing to see": "this isn't happening"}),
                content_type="application/json"
            )

    def get_success_url(self):
        return reverse('home')

    def get_object(self):
        return get_object_or_404(User, pk=self.request.user.id)


class RsvpListView(EditorRequiredMixin, ListView):
    model = Signup
    template_name = 'newswire/cp/rsvp_list.html'

    def get_context_data(self, **kwargs):
        context = super(RsvpListView, self).get_context_data(**kwargs)
        event_signups = []
        try:
            context['signups'] = Signup.objects.order_by('event', 'rsvp')
        except Signup.DoesNotExist:
            pass
        return context


class RsvpListViewRaw(EditorRequiredMixin, ListView):
    model = Signup
    template_name = 'newswire/cp/rsvp_list_raw.html'

    def get_context_data(self, **kwargs):
        context = super(RsvpListViewRaw, self).get_context_data(**kwargs)
        event_signups = []
        try:
            context['signups'] = Signup.objects.order_by('event', 'rsvp')
        except Signup.DoesNotExist:
            pass
        return context


class ControlPanelHomeView(EditorRequiredMixin, ListView, BulletinContextMixin):
    model = Announcement
    template_name = 'newswire/cp/home.html'

    def get_queryset(self):
        # do not show archived instances.
        qs = super(ListView, self).get_queryset()
        return qs


class GroupListView(EditorRequiredMixin, ListView):
    model = ExtendedGroup
    template_name = 'newswire/cp/extendedgroup_list.html'

    page = Context({
        'title': 'Groups - ',
        'header': 'Groups',
        'description': 'Lists all groups'
    })

    def get_context_data(self, **kwargs):
        context = super(GroupListView, self).get_context_data(**kwargs)
        context['page'] = self.page
        return context


class GroupCreateView(EditorRequiredMixin, CreateView):
    model = ExtendedGroup
    template_name = 'newswire/cp/extendedgroup_form.html'

    success_url = reverse_lazy('group_list')
    form_class = ExtendedGroupForm

    page = Context({
        'title': 'Create Group - ',
        'header': 'Create Group',
        'description': 'Use this to create new groups'
    })

    def get_context_data(self, **kwargs):
        context = super(GroupCreateView, self).get_context_data(**kwargs)
        context['page'] = self.page

        try:
            context['all_users_not_in_group'] = Profile.objects.all()
        except Profile.DoesNotExist:
            pass
        return context


class GroupUpdateView(EditorRequiredMixin, UpdateView):
    model = ExtendedGroup
    template_name = 'newswire/cp/extendedgroup_form.html'

    success_url = reverse_lazy('group_list')
    form_class = ExtendedGroupForm

    page = Context({
        'title': 'Update Group - ',
        'header': 'Update Group',
        'description': 'Use this to update group details'
    })

    def get_context_data(self, **kwargs):
        context = super(GroupUpdateView, self).get_context_data(**kwargs)
        context['page'] = self.page
        context['all_user_ids_in_group'] = self.object.member.values_list('id', flat=True)
        context['all_user_ids_in_group_leaders'] = self.object.leader.values_list('id', flat=True)

        try:
            context['all_users_not_in_group'] = Profile.objects.all()
        except Profile.DoesNotExist:
            pass
        return context


class GroupDeleteView(EditorRequiredMixin, DeleteView):
    model = ExtendedGroup
    template_name = 'newswire/cp/_base_delete.html'

    success_url = reverse_lazy('group_list')

    page = Context({
        'title': 'Delete Group - ',
        'header': 'Delete Group',
        'description': 'Use this to delete groups'
    })

    def get_context_data(self, **kwargs):
        context = super(GroupDeleteView, self).get_context_data(**kwargs)
        context['page'] = self.page
        return context


class GroupAttendanceListView(EditorRequiredMixin, ListView):
    model = GroupAttendance
    template_name = 'newswire/cp/group_attendance_list.html'

    page = Context({
        'title': 'Attendance - ',
        'header': 'Attendance',
        'description': 'Lists all attendance'
    })

    def get_context_data(self, **kwargs):
        context = super(GroupAttendanceListView, self).get_context_data(**kwargs)
        context['page'] = self.page
        return context


from django.forms import formset_factory, modelformset_factory
from django.forms.formsets import formset_factory
from newswire.forms import GroupAttendanceFormSetHelper


class GroupAttendanceCreateView(EditorRequiredMixin, TemplateView):
    model = GroupAttendance
    template_name = 'newswire/cp/group_attendance_form.html'
    success_url = reverse_lazy('groupattendance_list')
    form_class = formset_factory(GroupAttendance, GroupAttendanceForm, extra=3)

    page = Context({
        'title': 'Create Attendance - ',
        'header': 'Create Attendance',
        'description': 'Use this to create new attendance'
    })

    def get_context_data(self, **kwargs):
        context = super(GroupAttendanceCreateView, self).get_context_data(**kwargs)
        context['formset'] = formset_factory(GroupAttendance, GroupAttendanceForm, extra=0)
        context['formset2'] = modelformset_factory(GroupAttendance, fields=("__all__"), extra=0)
        context['helper'] = GroupAttendanceFormSetHelper()
        context['page'] = self.page
        return context


class GroupAttendanceUpdateView(EditorRequiredMixin, UpdateView):
    model = GroupAttendance
    template_name = 'newswire/cp/group_attendance_form.html'

    success_url = reverse_lazy('groupattendance_list')
    form_class = ExtendedGroupForm

    page = Context({
        'title': 'Update Attendance - ',
        'header': 'Update Attendance',
        'description': 'Use this to update attendance details'
    })

    def get_context_data(self, **kwargs):
        context = super(GroupAttendanceUpdateView, self).get_context_data(**kwargs)
        context['page'] = self.page
        return context


class GroupAttendanceDeleteView(EditorRequiredMixin, DeleteView):
    model = GroupAttendance
    template_name = 'newswire/cp/_base_delete.html'

    success_url = reverse_lazy('groupattendance_list')

    page = Context({
        'title': 'Delete Attendance - ',
        'header': 'Delete Attendance',
        'description': 'Use this to delete attendance'
    })

    def get_context_data(self, **kwargs):
        context = super(GroupAttendanceDeleteView, self).get_context_data(**kwargs)
        context['page'] = self.page
        return context
