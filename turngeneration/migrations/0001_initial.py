# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='GenerationRule',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('freq', models.PositiveSmallIntegerField(choices=[(0, b'Yearly'), (1, b'Monthly'), (2, b'Weekly'), (3, b'Daily'), (4, b'Hourly'), (5, b'Minutely')], blank=True, default=3)),
                ('dtstart', models.DateTimeField(null=True, blank=True)),
                ('interval', models.PositiveIntegerField(null=True, blank=True)),
                ('count', models.PositiveIntegerField(null=True, blank=True)),
                ('until', models.DateTimeField(null=True, blank=True)),
                ('bysetpos', models.CommaSeparatedIntegerField(blank=True, max_length=64)),
                ('bymonth', models.CommaSeparatedIntegerField(blank=True, max_length=64)),
                ('bymonthday', models.CommaSeparatedIntegerField(blank=True, max_length=64)),
                ('byyearday', models.CommaSeparatedIntegerField(blank=True, max_length=64)),
                ('byweekno', models.CommaSeparatedIntegerField(blank=True, max_length=64)),
                ('byweekday', models.CommaSeparatedIntegerField(blank=True, max_length=64)),
                ('byhour', models.CommaSeparatedIntegerField(blank=True, max_length=64)),
                ('byminute', models.CommaSeparatedIntegerField(blank=True, max_length=64)),
            ],
        ),
        migrations.CreateModel(
            name='GenerationTime',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('timestamp', models.DateTimeField(auto_now=True)),
            ],
            options={
                'get_latest_by': 'timestamp',
                'ordering': ['-timestamp'],
            },
        ),
        migrations.CreateModel(
            name='Generator',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
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
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
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
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
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
