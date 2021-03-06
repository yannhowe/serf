# Generated by Django 2.2.3 on 2019-07-06 04:54

import datetime
from django.conf import settings
import django.contrib.auth.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('newswire', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='extendedgroup',
            managers=[
                ('objects', django.contrib.auth.models.GroupManager()),
            ],
        ),
        migrations.AlterField(
            model_name='announcement',
            name='approver',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='announcement_approver', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='announcement',
            name='category',
            field=models.ForeignKey(blank=True, default='', null=True, on_delete=django.db.models.deletion.SET_NULL, to='newswire.Category', verbose_name='Audience'),
        ),
        migrations.AlterField(
            model_name='announcement',
            name='publish_end_date',
            field=models.DateField(default=datetime.datetime(2019, 7, 8, 0, 0), verbose_name='Date to end publishing'),
        ),
        migrations.AlterField(
            model_name='announcement',
            name='submitter',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='announcement_submitter', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='buildingfundcollection',
            name='building_fund_year_goal',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.SET_DEFAULT, to='newswire.BuildingFundYearGoal'),
        ),
        migrations.AlterField(
            model_name='buildingfundcollection',
            name='building_fund_year_pledge',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.SET_DEFAULT, to='newswire.BuildingFundYearPledge'),
        ),
        migrations.AlterField(
            model_name='groupattendance',
            name='group',
            field=models.ForeignKey(default=3, on_delete=django.db.models.deletion.SET_DEFAULT, to='newswire.ExtendedGroup'),
        ),
        migrations.AlterField(
            model_name='groupattendance',
            name='person',
            field=models.ForeignKey(default=3, on_delete=django.db.models.deletion.SET_DEFAULT, to='newswire.Profile'),
        ),
        migrations.AlterField(
            model_name='relationship',
            name='person',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='person_relationship', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='relationship',
            name='user',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='user_relationship', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='sundayattendance',
            name='approver',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_DEFAULT, related_name='sunday_attendance_approver', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='sundayattendance',
            name='submitter',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_DEFAULT, related_name='sunday_attendance_submitter', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='weeklyverse',
            name='date',
            field=models.DateField(default=datetime.datetime(2019, 7, 8, 0, 0)),
        ),
    ]
