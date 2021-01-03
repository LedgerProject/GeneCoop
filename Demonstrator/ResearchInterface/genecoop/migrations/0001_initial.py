# Generated by Django 3.1.4 on 2021-01-03 21:53

import datetime
from django.db import migrations, models
import django.db.models.deletion


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
                ('user_id', models.IntegerField(default=0)),
                ('token', models.CharField(max_length=2000, primary_key=True, serialize=False)),
                ('request_approved', models.DateTimeField(default=datetime.datetime(1900, 1, 1, 0, 0), verbose_name='date sent')),
                ('status', models.CharField(choices=[('NOT DONE', 'Consent has not been signed yet'), ('DONE', 'Consent has been signed')], default='NOT DONE', max_length=8)),
            ],
        ),
        migrations.CreateModel(
            name='Operation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('description', models.CharField(max_length=1000)),
                ('key', models.IntegerField(default=0, unique=True)),
                ('chosen_option', models.IntegerField(default=-1)),
            ],
        ),
        migrations.CreateModel(
            name='Option',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=200)),
                ('description', models.CharField(max_length=1000)),
                ('operation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='genecoop.operation')),
            ],
        ),
        migrations.CreateModel(
            name='Membership',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('consent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='genecoop.consent')),
                ('operation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='genecoop.operation')),
            ],
        ),
        migrations.AddField(
            model_name='consent',
            name='operations',
            field=models.ManyToManyField(through='genecoop.Membership', to='genecoop.Operation'),
        ),
    ]
