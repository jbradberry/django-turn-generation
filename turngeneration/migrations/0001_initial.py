# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='GenerationRule',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('freq', models.PositiveSmallIntegerField(default=3, blank=True, choices=[(0, b'Yearly'), (1, b'Monthly'), (2, b'Weekly'), (3, b'Daily'), (4, b'Hourly'), (5, b'Minutely')])),
                ('dtstart', models.DateTimeField(null=True, blank=True)),
                ('interval', models.PositiveIntegerField(null=True, blank=True)),
                ('count', models.PositiveIntegerField(null=True, blank=True)),
                ('until', models.DateTimeField(null=True, blank=True)),
                ('bysetpos', models.CommaSeparatedIntegerField(max_length=64, blank=True)),
                ('bymonth', models.CommaSeparatedIntegerField(max_length=64, blank=True)),
                ('bymonthday', models.CommaSeparatedIntegerField(max_length=64, blank=True)),
                ('byyearday', models.CommaSeparatedIntegerField(max_length=64, blank=True)),
                ('byweekno', models.CommaSeparatedIntegerField(max_length=64, blank=True)),
                ('byweekday', models.CommaSeparatedIntegerField(max_length=64, blank=True)),
                ('byhour', models.CommaSeparatedIntegerField(max_length=64, blank=True)),
                ('byminute', models.CommaSeparatedIntegerField(max_length=64, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='GenerationTime',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timestamp', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['-timestamp'],
                'get_latest_by': 'timestamp',
            },
        ),
        migrations.CreateModel(
            name='Generator',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('object_id', models.PositiveIntegerField()),
                ('generating', models.BooleanField(default=False)),
                ('generation_time', models.DateTimeField(null=True)),
                ('task_id', models.TextField()),
                ('force_generate', models.BooleanField(default=True)),
                ('autogenerate', models.BooleanField(default=True)),
                ('allow_pauses', models.BooleanField(default=True)),
                ('minimum_between_generations', models.PositiveIntegerField(null=True, blank=True)),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
            ],
        ),
        migrations.CreateModel(
            name='Pause',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('object_id', models.PositiveIntegerField()),
                ('timestamp', models.DateTimeField(auto_now=True)),
                ('reason', models.TextField()),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
                ('generator', models.ForeignKey(related_name='pauses', to='turngeneration.Generator')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Ready',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('object_id', models.PositiveIntegerField()),
                ('timestamp', models.DateTimeField(auto_now=True)),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
                ('generator', models.ForeignKey(related_name='readies', to='turngeneration.Generator')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
        migrations.AddField(
            model_name='generationtime',
            name='generator',
            field=models.ForeignKey(related_name='timestamps', to='turngeneration.Generator'),
        ),
        migrations.AddField(
            model_name='generationrule',
            name='generator',
            field=models.ForeignKey(related_name='rules', to='turngeneration.Generator'),
        ),
        migrations.AlterUniqueTogether(
            name='ready',
            unique_together=set([('content_type', 'object_id', 'generator')]),
        ),
        migrations.AlterUniqueTogether(
            name='pause',
            unique_together=set([('content_type', 'object_id', 'generator')]),
        ),
        migrations.AlterUniqueTogether(
            name='generator',
            unique_together=set([('content_type', 'object_id')]),
        ),
    ]
