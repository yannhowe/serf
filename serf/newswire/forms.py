from django.forms import ModelForm
from django.forms.formsets import BaseFormSet
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, HTML, Field, Button
from crispy_forms.bootstrap import FormActions, PrependedText, InlineRadios

from django.contrib.auth.models import User
from django import forms
from newswire.models import OrderOfService, Announcement, Category, Event, Profile, WeeklyVerse, SundayAttendance, BuildingFundCollection, BuildingFundYearPledge, BuildingFundYearGoal, ExtendedGroup, GroupAttendance


from django.forms.models import modelformset_factory


class UserFormFrontEndForm(ModelForm):

    class Meta:
        model = User
        fields = ['first_name', 'last_name']


class ProfileFrontEndForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(ProfileFrontEndForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            Field(
                'first_name',
                'last_name'
            ),
            PrependedText('email', '<i class="fa fa-envelope"></i>',
                          type="email"),
            Field(
                'prefered_name',
                'maiden_name',
                'gender'
            ),
            PrependedText('date_of_birth', '<i class="fa fa-calendar"></i>',
                          css_class="dateinput"),
            PrependedText('date_of_marriage', '<i class="fa fa-calendar"></i>',
                          css_class="dateinput"),
            PrependedText('date_of_baptism', '<i class="fa fa-calendar"></i>',
                          css_class="dateinput"),
            PrependedText('date_of_death', '<i class="fa fa-calendar"></i>',
                          css_class="dateinput"),
            PrependedText('mobile_number', '<i class="fa fa-phone"></i>',
                          type="text",),
            PrependedText('home_number', '<i class="fa fa-phone"></i>',
                          type="text",),
            Field(
                'address_block',
                'address_street',
                'address_unit',
                'country',
                'postal_code'
            ),
            FormActions(
                Submit('save', 'Save changes'),
                HTML(
                    '<a class="btn" href={% url "profile_front_end_detail" %}>Cancel</a>'),
            )
        )
        gender = forms.ChoiceField(choices=(('M', 'Male'), ('F', 'Female')))

    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'prefered_name', 'maiden_name', 'gender', 'date_of_birth', 'date_of_marriage', 'date_of_baptism',
                  'mobile_number', 'home_number', 'address_block', 'address_street', 'address_unit', 'country', 'postal_code']


class ProfileForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.fields['user'].label = "Account to Attach this Profile to"
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            Field(
                'first_name',
                'last_name',
            ),
            Field('user', css_class='select_user_to_attach'),
            PrependedText('email', '<i class="fa fa-envelope"></i>',
                          type="email"),
            Field(
                'prefered_name',
                'maiden_name',
            ),
            InlineRadios('gender'),
            PrependedText('date_of_birth', '<i class="fa fa-calendar"></i>',
                          css_class="dateinput"),
            PrependedText('date_of_marriage', '<i class="fa fa-calendar"></i>',
                          css_class="dateinput"),
            PrependedText('date_of_baptism', '<i class="fa fa-calendar"></i>',
                          css_class="dateinput"),
            PrependedText('date_of_death', '<i class="fa fa-calendar"></i>',
                          css_class="dateinput"),
            PrependedText('mobile_number', '<i class="fa fa-phone"></i>',
                          type="text",),
            PrependedText('home_number', '<i class="fa fa-phone"></i>',
                          type="text",),
            Field(
                'address_block',
                'address_street',
                'address_unit',
                'country',
                'postal_code',
                'is_regular',
                'is_member'
            ),
            FormActions(
                Submit('save', 'Save changes'),
                HTML(
                    '<a class="btn" href={% url "profile_list" %}>Cancel</a>'),
            )
        )
        gender = forms.ChoiceField(choices=(('M', 'Male'), ('F', 'Female')))

    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'user', 'email', 'prefered_name', 'maiden_name', 'gender', 'date_of_birth', 'date_of_marriage', 'date_of_baptism',
                  'date_of_death', 'mobile_number', 'home_number', 'address_block', 'address_street', 'address_unit', 'country', 'postal_code', 'is_regular', 'is_member']


class AttendanceForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(AttendanceForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)

        self.helper.layout = Layout(
            PrependedText('date', '<i class="fa fa-calendar"></i>',
                          css_class="dateinput"),
            Field('english_congregation',
                  'chinese_congregation',
                  'childrens_church',
                  'preschoolers',
                  'nursery',
                  'under_review',
                  'notes'
                  ),
            FormActions(
                Submit('save', 'Save changes'),
                HTML(
                    '<a class="btn" href={% url "attendance_summary" %}>Cancel</a>'),
            )
        )

    class Meta:
        model = SundayAttendance
        exclude = ['submitter', 'approver']


class AttendanceFormFrontEnd(ModelForm):

    def __init__(self, *args, **kwargs):
        super(AttendanceFormFrontEnd, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)

        self.helper.layout = Layout(
            PrependedText('date', '<i class="fa fa-calendar"></i>',
                          css_class="dateinput"),
            Field('english_congregation',
                  'chinese_congregation',
                  'childrens_church',
                  'preschoolers',
                  'nursery',
                  'notes'
                  ),
            FormActions(
                Submit('save', 'Save changes'),
                HTML(
                    '<a class="btn" href={% url "under_review_front_end" %}>Cancel</a>'),
            )
        )

    class Meta:
        model = SundayAttendance
        exclude = ['submitter', 'approver', 'under_review']


class WeeklyVerseForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(WeeklyVerseForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)

        self.helper.layout.append(
            FormActions(
                Submit('save', 'Save changes'),
                HTML(
                    '<a class="btn" href={% url "weeklyverse_list" %}>Cancel</a>'),
            )
        )

    class Meta:
        model = WeeklyVerse
        fields = '__all__'


class OrderOfServiceForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(OrderOfServiceForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            Field('service_name'),
            PrependedText('date', '<i class="fa fa-calendar"></i>',
                          css_class="dateinput"),
            Field('text'),
            FormActions(
                Submit('save', 'Save changes'),
                HTML(
                    '<a class="btn" href={% url "orderofservice_list" %}>Cancel</a>'),
            )
        )

    class Meta:
        model = OrderOfService
        fields = ['date', 'text', 'service_name']


class AnnouncementForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(AnnouncementForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            Field('title', 'body'),
            PrependedText(
                'publish_start_date', '<i class="fa fa-calendar"></i>', css_class="dateinput"),
            PrependedText(
                'publish_end_date', '<i class="fa fa-calendar"></i>', css_class="dateinput"),
            Field('category', 'link', ),
            Field('hidden', title="Hide this Announcement"),
            Field('under_review', title="Under review"),
            Field('contact'),

            FormActions(
                Submit('save', 'Save changes'),
                HTML(
                    '<a class="btn" href={% url "announcement_list" %}>Cancel</a>'),
            )
        )

    class Meta:
        model = Announcement
        exclude = ['user']


class AnnouncementFormFrontEnd(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(AnnouncementFormFrontEnd, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            Field('title', 'body'),
            PrependedText(
                'publish_start_date', '<i class="fa fa-calendar"></i>', css_class="dateinput"),
            PrependedText(
                'publish_end_date', '<i class="fa fa-calendar"></i>', css_class="dateinput"),
            Field('category', 'link', ),
            Field('contact'),
            FormActions(
                Submit('save', 'Save changes'),
                HTML(
                    '<a class="btn" href={% url "under_review_front_end" %}>Cancel</a>'),
            )
        )

    class Meta:
        model = Announcement
        exclude = ['submitter', 'approver', 'hidden', 'under_review']


class CategoryForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(CategoryForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            Field('name', 'description'),
            Field('color', css_class="color-picker-1"),
            FormActions(
                Submit('save', 'Save changes'),
                HTML(
                    '<a class="btn" href={% url "announcement_list" %}>Cancel</a>'),
            )
        )

    class Meta:
        model = Category
        fields = ['name', 'description', 'color']


class EventForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(EventForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            Field('title'),
            Field('description'),
            PrependedText('date_start', '<i class="fa fa-calendar"></i>',
                          css_class="dateinput"),
            PrependedText('date_end', '<i class="fa fa-calendar"></i>',
                          css_class="dateinput"),
            Field('display_override', title="Display"),
            Field('track_rsvp', title="Enable RSVP"),
            FormActions(
                Submit('save', 'Save changes'),
                HTML(
                    '<a class="btn" href={% url "event_list" %}>Cancel</a>'),
            )
        )

    class Meta:
        model = Event
        fields = ['title', 'description', 'date_start', 'date_end', 'display_override', 'track_rsvp']


class BuildingFundCollectionForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(BuildingFundCollectionForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        try:
            latestBuildingFundYearPledge = BuildingFundYearPledge.objects.latest('date')
        except BuildingFundYearPledge.DoesNotExist:
            latestBuildingFundYearPledge = None
        try:
            latestBuildingFundYearGoal = BuildingFundYearGoal.objects.latest('date')
        except BuildingFundYearGoal.DoesNotExist:
            latestBuildingFundYearGoal = None

        self.initial = {
            'building_fund_year_pledge': latestBuildingFundYearPledge,
            'building_fund_year_goal': latestBuildingFundYearGoal
        }

        self.helper.layout.append(
            FormActions(
                Submit('save', 'Save changes'),
                HTML(
                    '<a class="btn" href={% url "buildingfund_list" %}>Cancel</a>'),
            )
        )

    class Meta:
        model = BuildingFundCollection
        fields = '__all__'


class BuildingFundYearPledgeForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(BuildingFundYearPledgeForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)

        self.helper.layout.append(
            FormActions(
                Submit('save', 'Save changes'),
                HTML(
                    '<a class="btn" href={% url "buildingfund_list" %}>Cancel</a>'),
            )
        )

    class Meta:
        model = BuildingFundYearPledge
        fields = '__all__'


class BuildingFundYearGoalForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(BuildingFundYearGoalForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)

        self.helper.layout.append(
            FormActions(
                Submit('save', 'Save changes'),
                HTML(
                    '<a class="btn" href={% url "buildingfund_list" %}>Cancel</a>'),
            )
        )

    class Meta:
        model = BuildingFundYearGoal
        fields = '__all__'


class ExtendedGroupForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(ExtendedGroupForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            Field('name', title="Group Type"),
            Field('group_type', title="Group Type"),
            Field('notes', title="Notes"),
            PrependedText('date_formed', '<i class="fa fa-calendar"></i>',
                          css_class="dateinput"),
            PrependedText('date_dissolved', '<i class="fa fa-calendar"></i>',
                          css_class="dateinput"),
            Field('meeting_day', title="Display"),
            PrependedText('meeting_time', '<i class="fa fa-clock-o"></i>',
                          css_class="timeinput", title='Time in 24 hour format (eg. 13:00 for 1pm)'),
            Field('active', title="Active Group"),
            Field('leader', css_class="select_leaders", title="Leader(s)"),
            Field('member', css_class="select_members", title="Member(s)"),
            FormActions(
                Submit('save', 'Save changes'),
                HTML(
                    '<a class="btn" href={% url "group_list" %}>Cancel</a>'),
            )
        )

    class Meta:
        model = ExtendedGroup
        fields = ['leader', 'name', 'group_type', 'notes', 'date_formed', 'date_dissolved', 'meeting_day', 'meeting_time', 'active', 'member']


class GroupAttendanceForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(GroupAttendanceForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_tag = False

    class Meta:
        model = GroupAttendance
        fields = '__all__'


class GroupAttendanceForm2(forms.Form):
    person = forms.ModelChoiceField(Profile.objects.all())
    group = forms.ModelChoiceField(ExtendedGroup.objects.all())
    date = forms.DateField()
    attendance = forms.IntegerField()


class GroupAttendanceFormSetHelper(FormHelper):

    def __init__(self, *args, **kwargs):
        super(GroupAttendanceFormSetHelper, self).__init__(*args, **kwargs)
        self.form_method = 'post'
        self.layout = Layout(
            'person',
            'group',
            'date',
            'attendance',
        )
        self.render_required_fields = True
