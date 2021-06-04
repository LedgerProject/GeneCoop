# Generated by Django 3.1.8 on 2021-06-04 08:03

import datetime
from django.db import migrations, models
import django.db.models.deletion
from django.utils.timezone import utc


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Consent',
            fields=[
                ('name', models.CharField(max_length=200)),
                ('description', models.CharField(max_length=1000)),
                ('user_id', models.CharField(default='', max_length=50)),
                ('experiments', models.CharField(default='', max_length=1000)),
                ('token', models.CharField(max_length=50, primary_key=True, serialize=False, unique=True)),
                ('signed_vc', models.CharField(max_length=20000)),
                ('consent_created', models.DateTimeField(default=datetime.datetime(1899, 12, 31, 23, 40, tzinfo=utc), verbose_name='date created')),
                ('consent_signed', models.DateTimeField(default=datetime.datetime(1899, 12, 31, 23, 40, tzinfo=utc), verbose_name='date signed')),
                ('status', models.CharField(choices=[('NOT DONE', 'Consent has not been signed yet'), ('DONE', 'Consent has been signed')], default='NOT DONE', max_length=8)),
            ],
        ),
        migrations.CreateModel(
            name='ConsentLogger',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.CharField(max_length=500)),
                ('request_received', models.DateTimeField(default=datetime.datetime(1899, 12, 31, 23, 40, tzinfo=utc), verbose_name='date received')),
                ('type', models.CharField(choices=[('IS SIGNED?', 'Request to check whether consent is signed'), ('ALLOWED EXPERIMENTS', 'Request to check what experiments are allowed'), ('LOG EXPERIMENT', 'Request to log experiment'), ('LOG NOT SIGNED EXPERIMENT', 'Request to log experiment which is not signed')], default='', max_length=30)),
                ('consent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='donor_app.consent')),
            ],
        ),
    ]
