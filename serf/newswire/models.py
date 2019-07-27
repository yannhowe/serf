from django.db import models
from django.contrib.auth.admin import User
from django.contrib.auth.models import Group, User
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.shortcuts import get_object_or_404
from paintstore.fields import ColorPickerField
from datetime import datetime, timedelta
import calendar
from django.utils import timezone
import datetime

from django.forms import ModelForm, TextInput, DateInput
from suit.widgets import EnclosedInput, SuitDateWidget, SuitSplitDateTimeWidget

from django.db.models.signals import post_save
from django.dispatch import receiver

from constance import config


class Category(models.Model):

    class Meta:
        verbose_name_plural = "categories"

    name = models.CharField(max_length=80)
    description = models.TextField(max_length=1200)
    color = ColorPickerField()

    def __str__(self):
        return self.name


def get_today():
    return datetime.datetime(timezone.now().year, timezone.now().month, timezone.now().day)


def get_coming_monday(date=get_today()):
    # coming monday's date
    coming_monday = date
    while coming_monday.weekday() != 0:
        coming_monday += datetime.timedelta(1)
    return coming_monday


# Stores announcements for newsvine


class Announcement(models.Model):
    submitter = models.ForeignKey(User, db_index=True, related_name="announcement_submitter", null=True, blank=True, default=None, on_delete=models.SET_NULL)
    approver = models.ForeignKey(User, db_index=True, related_name="announcement_approver", null=True, blank=True, default=None, on_delete=models.SET_NULL)
    title = models.CharField(max_length=200, default='')
    body = models.TextField(max_length=1200, default='')
    publish_start_date = models.DateField('Date to start publishing', default=datetime.datetime.now)
    publish_end_date = models.DateField('Date to end publishing', default=get_coming_monday())
    category = models.ForeignKey(Category, default='', verbose_name='Audience', on_delete=models.SET_NULL, null=True, blank=True,)
    link = models.CharField(max_length=400, blank=True, default='')
    hidden = models.BooleanField(default=False)
    under_review = models.BooleanField(default=True)
    contact = models.CharField(max_length=200, blank=True, default='')

    def is_published(self):
        import datetime
        today = datetime.date.today()
        if self.publish_start_date <= today <= self.publish_end_date:
            return True
        return False

    def __str__(self):
        return '%s - %s: %s' % (self.publish_start_date, self.publish_end_date, self.title)

# Stores event list


class Event(models.Model):
    # Display Override
    DEFAULT = 'default'
    HIDE = 'hide'
    SHOW = 'show'
    CHOICES = (
        (DEFAULT, 'Default: Displays 14 days in advance'),
        (HIDE, 'Hide Event'),
        (SHOW, 'Show Event'),
    )

    title = models.CharField(max_length=200)
    description = models.TextField(max_length=400, null=True, blank=True)
    date_start = models.DateField(default=datetime.datetime.now)
    date_end = models.DateField(blank=True, null=True)
    track_rsvp = models.BooleanField(default=False)
    display_override = models.CharField(max_length=30, choices=CHOICES, default=CHOICES[0][0], null=True, blank=True)

    def __str__(self):
        return '%s - %s to %s' % (self.title, self.date_start, self.date_end)


class Signup(models.Model):
    # Service Names
    NOTGOING = 'notgoing'
    INTERESTED = 'interested'
    GOING = 'going'
    CHOICES = (
        (NOTGOING, 'Not Going'),
        (INTERESTED, 'Interested'),
        (GOING, 'Going')
    )

    user = models.ForeignKey(User, db_index=True,  on_delete=models.CASCADE)
    event = models.ForeignKey(Event, db_index=True, on_delete=models.CASCADE)
    rsvp = models.CharField(max_length=30, choices=CHOICES, default=CHOICES[0][0])

    def __str__(self):
        return '%s - %s - %s' % (self.event, self.user, self.rsvp)


# Stores announcements for newsvine


class OrderOfService(models.Model):
    # Service Names
    SUN_MORN_ENG = 'sunday-morning-english'
    CHOICES = (
        (SUN_MORN_ENG, 'Sunday Morning - English Service'),)

    date = models.DateField(default=datetime.datetime.now)
    text = models.TextField(default='', blank=True)
    service_name = models.CharField(
        max_length=200, choices=CHOICES, default=CHOICES[0][0])

    def is_upcoming(self):
        import datetime
        today = datetime.date.today()
        if today <= self.date:
            return True
        return False

    def is_print(self):
        import datetime
        # coming sunday's date
        coming_sunday = datetime.date.today()
        while coming_sunday.weekday() != 6:
            coming_sunday += datetime.timedelta(1)

        if coming_sunday == self.date:
            return True
        return False

    def num_of_lines(self):
        i = 0
        for line in self.text:
            if "\n" in line:
                i += 1
        return i

    def get_absolute_url(self):
        return reverse('orderofservice_edit', kwargs={'pk': self.pk})

    def __str__(self):
        return '%s %s' % (self.date, self.service_name)


# Add member details
class Profile(models.Model):
    M = 'm'
    F = 'f'
    GENDER_CHOICES = (
        (M, 'Male'),
        (F, 'Female'),
    )

    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
    first_name = models.CharField("First Name", max_length=80, null=True, blank=True)
    last_name = models.CharField("Last Name", max_length=80, null=True, blank=True)
    email = models.EmailField("Email Address", max_length=254, null=True, blank=True)

    prefered_name = models.CharField("Preferred Name", max_length=120, null=True, blank=True, help_text="We will use this name around the site instead of a combination of last+first name.")
    maiden_name = models.CharField("Maiden Name", max_length=80, null=True, blank=True)

    gender = models.CharField("Gender", max_length=1, choices=GENDER_CHOICES, null=True, blank=True)

    date_record_updated = models.DateField(null=True, blank=True, default=datetime.datetime.now)

    # important dates
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_marriage = models.DateField(null=True, blank=True)
    date_of_baptism = models.DateField(null=True, blank=True)
    date_of_death = models.DateField(null=True, blank=True)

    mobile_number = models.CharField(max_length=15, null=True, blank=True)
    home_number = models.CharField(max_length=15, null=True, blank=True)

    # address
    address_block = models.CharField(max_length=12, null=True, blank=True)
    address_street = models.CharField(max_length=140, null=True, blank=True)
    address_unit = models.CharField(max_length=12, null=True, blank=True)
    country = models.CharField(max_length=30, null=True, blank=True)
    postal_code = models.CharField(max_length=12, null=True, blank=True)

    # other details
    is_regular = models.BooleanField(default=True)
    is_member = models.BooleanField(default=False)

    def __str__(self):
        return '%s, %s %s' % (self.user, self.first_name, self.last_name)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.email == None:
            return none
        else:
            editor_list = config.EDITOR_LIST.split()
            try:
                if any(instance.email in s for s in editor_list):
                    instance.groups.add(Group.objects.get(name='editor'))
            except Group.DoesNotExist:
                pass

            contributor_list = config.CONTRIBUTOR_LIST.split()
            try:
                if any(instance.email in s for s in contributor_list):
                    instance.groups.add(Group.objects.get(name='contributor'))
            except Group.DoesNotExist:
                pass

            email_matching = Profile.objects.filter(email=instance.email).first()
            if email_matching != None:
                email_matching.user = instance
                email_matching.save()
                instance.first_name = email_matching.first_name
                instance.last_name = email_matching.last_name
                instance.save()
            else:
                Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

# family relationships


class Relationship(models.Model):
    MEMBER_RELATIONSHIP_CHOICES = (
        ('MO', 'Mother'),
        ('FA', 'Father'),
        ('BRO', 'Brother'),
        ('SIS', 'Sister'),
        ('SON', 'Son'),
        ('DAUG', 'Daughter'),
        ('GRMA', 'Grand Mother'),
        ('GRFA', 'Grand Father'),
        ('GRSON', 'Grand Son'),
        ('GRDAUG', 'Grand Daughter'),
    )

    user = models.OneToOneField(User, null=True, related_name='user_relationship', on_delete=models.SET_NULL)
    person = models.ForeignKey(User, null=True, related_name='person_relationship', on_delete=models.SET_NULL)
    relationship = models.CharField(max_length=10, choices=MEMBER_RELATIONSHIP_CHOICES)

    def __str__(self):
        return '%s, %s, %s' % (self.person, self.user, self.relationship)


class SundayAttendance(models.Model):
    submitter = models.ForeignKey(User, db_index=True, related_name="sunday_attendance_submitter", null=True, blank=True, default=None, on_delete=models.SET_DEFAULT)
    approver = models.ForeignKey(User, db_index=True, related_name="sunday_attendance_approver", null=True, blank=True, default=None, on_delete=models.SET_DEFAULT)
    date = models.DateField(default=datetime.datetime.now)
    english_congregation = models.PositiveSmallIntegerField(default=0)
    chinese_congregation = models.PositiveSmallIntegerField(default=0)
    childrens_church = models.PositiveSmallIntegerField(default=0)
    preschoolers = models.PositiveSmallIntegerField(default=0)
    nursery = models.PositiveSmallIntegerField(default=0)
    under_review = models.BooleanField(default=True)
    notes = models.TextField(max_length=300, null=True, blank=True)

    def __str__(self):
        return '%s' % (self.date)


class BuildingFundYearGoal(models.Model):
    name = models.TextField(max_length=80, null=True, blank=True)
    date = models.DateField(default=datetime.datetime.now)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default='0')
    description = models.TextField(max_length=300, null=True, blank=True)

    def __str__(self):
        formatted_amount = '{:20,.2f}'.format(self.amount)
        return '%s - $%s' % (self.date, formatted_amount)


class BuildingFundYearPledge(models.Model):
    name = models.TextField(max_length=80, null=True, blank=True)
    date = models.DateField(default=datetime.datetime.now)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default='0')
    description = models.TextField(max_length=300, null=True, blank=True)

    def __str__(self):
        formatted_amount = '{:20,.2f}'.format(self.amount)
        return '%s - $%s' % (self.date, formatted_amount)


class BuildingFundCollection(models.Model):
    date = models.DateField(default=datetime.datetime.now)
    building_fund_year_pledge = models.ForeignKey(BuildingFundYearPledge, on_delete=models.SET_DEFAULT, default=0)
    building_fund_year_goal = models.ForeignKey(BuildingFundYearGoal, on_delete=models.SET_DEFAULT, default=0)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default='0')
    notes = models.TextField(max_length=300, null=True, blank=True)

    def __str__(self):
        formatted_amount = '{:20,.2f}'.format(self.amount)
        return '%s - $%s' % (self.date.strftime("%d/%m/%y"), formatted_amount)


class WeeklyVerse(models.Model):
    date = models.DateField(default=get_coming_monday())
    verse = models.TextField(max_length=1200, default='')
    reference = models.CharField(max_length=40, default='')

    def __str__(self):
        return '%s - %s' % (self.date, self.reference)


class ExtendedGroup(Group):
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6
    IRREGULAR = 7

    DAYS_OF_WEEK = (
        (MONDAY, 'Monday'),
        (TUESDAY, 'Tuesday'),
        (WEDNESDAY, 'Wednesday'),
        (THURSDAY, 'Thursday'),
        (FRIDAY, 'Friday'),
        (SATURDAY, 'Saturday'),
        (SUNDAY, 'Sunday'),
        (IRREGULAR, 'Irregular'),
    )

    COMMUNITY = 0
    MANAGEMENT = 1
    COMMITTEE = 2

    GROUP_TYPE = (
        (COMMUNITY, 'Community Group'),
        (MANAGEMENT, 'Management'),
        (COMMITTEE, 'Committee'),
    )

    leader = models.ManyToManyField(Profile, blank=True, related_name='leader_profile')
    group_type = models.IntegerField(choices=GROUP_TYPE)
    notes = models.TextField(max_length=300, null=True, blank=True)
    date_formed = models.DateField(default=datetime.datetime.now, null=True, blank=True)
    date_dissolved = models.DateField(null=True, blank=True)
    meeting_day = models.IntegerField(choices=DAYS_OF_WEEK, null=True, blank=True, help_text="Day of the week the group regularly meets if any")
    meeting_time = models.TimeField(null=True, blank=True, help_text="Meeting time of the the group in 24hr format ie. 13:00 for 1pm")
    active = models.BooleanField(default=True)
    member = models.ManyToManyField(Profile, blank=True, related_name='leader_member')

    def __str__(self):
        return '%s' % (self.name)


class GroupAttendance(models.Model):
    PRESENT = 0
    ABSENT = 1
    EXCUSED = 2
    UNKNOWN = 3

    ATTENDANCE_CHOICES = (
        (PRESENT, 'Present'),
        (ABSENT, 'Absent'),
        (EXCUSED, 'Excused'),
        (UNKNOWN, 'Unknown'),
    )

    person = models.ForeignKey(Profile, on_delete=models.SET_DEFAULT, default=3)
    group = models.ForeignKey(ExtendedGroup, on_delete=models.SET_DEFAULT, default=3)
    date = models.DateField(default=datetime.datetime.now)
    attendance = models.IntegerField(choices=ATTENDANCE_CHOICES)

    def __str__(self):
        return '%s , %s , %s , %s' % (self.person.first_name, self.group, self.date, self.attendance)
