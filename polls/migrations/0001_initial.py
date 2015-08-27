# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('docfile', models.FileField(blank=True, upload_to='documents')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Plot',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('pdf', models.FileField(blank=True, upload_to='documents')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('activation_key', models.CharField(max_length=40)),
                ('key_expires', models.DateTimeField(default=datetime.date(2015, 8, 20))),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='plot',
            name='user_profile',
            field=models.ForeignKey(to='polls.UserProfile'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='document',
            name='user_profile',
            field=models.ForeignKey(to='polls.UserProfile'),
            preserve_default=True,
        ),
    ]
