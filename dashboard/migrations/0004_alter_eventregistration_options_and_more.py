# Generated by Django 5.1.4 on 2024-12-18 12:03

import django.core.validators
import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0003_alter_eventregistration_options_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='eventregistration',
            options={},
        ),
        migrations.AlterModelOptions(
            name='transportdetails',
            options={},
        ),
        migrations.RemoveField(
            model_name='attendee',
            name='id_proof',
        ),
        migrations.RemoveField(
            model_name='attendee',
            name='mobile',
        ),
        migrations.RemoveField(
            model_name='eventregistration',
            name='attending',
        ),
        migrations.RemoveField(
            model_name='eventregistration',
            name='created_at',
        ),
        migrations.RemoveField(
            model_name='eventregistration',
            name='event',
        ),
        migrations.RemoveField(
            model_name='eventregistration',
            name='mobile',
        ),
        migrations.RemoveField(
            model_name='eventregistration',
            name='updated_at',
        ),
        migrations.RemoveField(
            model_name='transportdetails',
            name='arrival_datetime',
        ),
        migrations.RemoveField(
            model_name='transportdetails',
            name='arrival_details',
        ),
        migrations.RemoveField(
            model_name='transportdetails',
            name='arrival_mode',
        ),
        migrations.RemoveField(
            model_name='transportdetails',
            name='departure_datetime',
        ),
        migrations.RemoveField(
            model_name='transportdetails',
            name='departure_details',
        ),
        migrations.RemoveField(
            model_name='transportdetails',
            name='departure_mode',
        ),
        migrations.AddField(
            model_name='attendee',
            name='identification_proof',
            field=models.CharField(choices=[('adhar_card', 'Adhar Card'), ('passport', 'Passport'), ('driving_license', 'Driving License')], default='adhar_card', max_length=50, verbose_name='Identification Proof'),
        ),
        migrations.AddField(
            model_name='attendee',
            name='mobile_number',
            field=models.CharField(default='', max_length=15, verbose_name='Participant Mobile Number'),
        ),
        migrations.AddField(
            model_name='eventregistration',
            name='flag_attending',
            field=models.CharField(choices=[('yes', 'Yes, I will attend the event'), ('no', "Sorry, I can't attend the event")], default='no', max_length=50, verbose_name='Will you attend?'),
        ),
        migrations.AddField(
            model_name='eventregistration',
            name='mobile_number',
            field=models.CharField(default='', max_length=15, verbose_name='Mobile Number'),
        ),
        migrations.AddField(
            model_name='eventregistration',
            name='number_of_people',
            field=models.PositiveIntegerField(default=0, help_text='Fill only if attending', verbose_name='Number of People Attending'),
        ),
        migrations.AddField(
            model_name='transportdetails',
            name='arrival_time',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='Arrival Time'),
        ),
        migrations.AddField(
            model_name='transportdetails',
            name='bus_number',
            field=models.CharField(blank=True, help_text='Optional for bus transport', max_length=50, null=True, verbose_name='Bus Number'),
        ),
        migrations.AddField(
            model_name='transportdetails',
            name='bus_stop',
            field=models.CharField(blank=True, help_text='Required if mode of transport is bus', max_length=100, null=True, verbose_name='Bus Stop'),
        ),
        migrations.AddField(
            model_name='transportdetails',
            name='departure_date',
            field=models.DateField(default=django.utils.timezone.now, verbose_name='Departure Date'),
        ),
        migrations.AddField(
            model_name='transportdetails',
            name='departure_time',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='Departure Time'),
        ),
        migrations.AddField(
            model_name='transportdetails',
            name='flight_number',
            field=models.CharField(blank=True, help_text='Required if mode of transport is flight', max_length=50, null=True, verbose_name='Flight Number'),
        ),
        migrations.AddField(
            model_name='transportdetails',
            name='mode_of_transport',
            field=models.CharField(choices=[('flight', 'Flight'), ('train', 'Train'), ('bus', 'Bus'), ('self', 'Self')], default='self', max_length=10, verbose_name='Mode of Transport'),
        ),
        migrations.AddField(
            model_name='transportdetails',
            name='terminal_name',
            field=models.CharField(blank=True, help_text='Required if mode of transport is flight', max_length=100, null=True, verbose_name='Terminal Name'),
        ),
        migrations.AddField(
            model_name='transportdetails',
            name='train_arrival_station',
            field=models.CharField(blank=True, help_text='Required if mode of transport is train', max_length=100, null=True, verbose_name='Train Arrival Station'),
        ),
        migrations.AddField(
            model_name='transportdetails',
            name='train_number',
            field=models.CharField(blank=True, help_text='Required if mode of transport is train', max_length=50, null=True, verbose_name='Train Number'),
        ),
        migrations.AlterField(
            model_name='attendee',
            name='name',
            field=models.CharField(default='', max_length=255, verbose_name='Participant Name'),
        ),
        migrations.AlterField(
            model_name='attendee',
            name='registration',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='participants', to='dashboard.eventregistration'),
        ),
        migrations.AlterField(
            model_name='eventregistration',
            name='country_code',
            field=models.CharField(default='+91', max_length=4, validators=[django.core.validators.RegexValidator(message='Country code must start with "+" and contain up to 3 digits.', regex='^\\+\\d{1,3}$')], verbose_name='Country Code'),
        ),
        migrations.AlterField(
            model_name='eventregistration',
            name='name',
            field=models.CharField(default='', max_length=255, verbose_name='Full Name'),
        ),
        migrations.AlterField(
            model_name='eventregistration',
            name='remarks',
            field=models.TextField(blank=True, help_text='Optional field for additional remarks.', null=True, verbose_name='Remarks'),
        ),
        migrations.AlterField(
            model_name='transportdetails',
            name='registration',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transport_details', to='dashboard.eventregistration'),
        ),
    ]
