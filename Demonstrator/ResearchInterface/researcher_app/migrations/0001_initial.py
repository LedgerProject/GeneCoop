# Generated by Django 3.1.8 on 2021-06-01 16:18

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
from django.utils.timezone import utc


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Researcher',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=1000)),
                ('institute', models.CharField(max_length=200)),
                ('institute_publickey', models.CharField(max_length=500)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Request',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('description', models.CharField(max_length=1000)),
                ('experiments', models.CharField(default='', max_length=1000)),
                ('token', models.CharField(max_length=50, unique=True)),
                ('token_time', models.FloatField(default=0)),
                ('token_signature', models.CharField(default='', max_length=500)),
                ('request_sent', models.DateTimeField(default=datetime.datetime(1899, 12, 31, 23, 40, tzinfo=utc), verbose_name='date sent')),
                ('request_checked', models.DateTimeField(default=datetime.datetime(1899, 12, 31, 23, 40, tzinfo=utc), verbose_name='date signed')),
                ('status', models.CharField(choices=[('NOT SENT', 'Request has not been sent'), ('SENT', 'Request has been sent'), ('NOT REPLIED', 'Request has not been replied'), ('REPLIED', 'Request has been replied')], default='NOT SENT', max_length=15)),
                ('researcher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='researcher_app.researcher')),
            ],
        ),
    ]
