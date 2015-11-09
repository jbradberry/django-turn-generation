# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Removing unique constraint on 'GenerationTime', fields ['content_type', 'object_id']
        db.delete_unique(u'turngeneration_generationtime', ['content_type_id', 'object_id'])

        # Deleting model 'GenerationTime'
        db.delete_table(u'turngeneration_generationtime')

        # Adding model 'Generator'
        db.create_table(u'turngeneration_generator', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('generation_time', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('task_id', self.gf('django.db.models.fields.TextField')()),
            ('autogenerate', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('allow_pauses', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('minimum_between_generations', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'turngeneration', ['Generator'])

        # Adding unique constraint on 'Generator', fields ['content_type', 'object_id']
        db.create_unique(u'turngeneration_generator', ['content_type_id', 'object_id'])


        # Changing field 'GenerationRule.generator'
        db.alter_column(u'turngeneration_generationrule', 'generator_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['turngeneration.Generator']))

        # Changing field 'Ready.generator'
        db.alter_column(u'turngeneration_ready', 'generator_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['turngeneration.Generator']))

        # Changing field 'Pause.generator'
        db.alter_column(u'turngeneration_pause', 'generator_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['turngeneration.Generator']))

    def backwards(self, orm):
        # Removing unique constraint on 'Generator', fields ['content_type', 'object_id']
        db.delete_unique(u'turngeneration_generator', ['content_type_id', 'object_id'])

        # Adding model 'GenerationTime'
        db.create_table(u'turngeneration_generationtime', (
            ('minimum_between_generations', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
            ('task_id', self.gf('django.db.models.fields.TextField')()),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('generation_time', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('allow_pauses', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('autogenerate', self.gf('django.db.models.fields.BooleanField')(default=True)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal(u'turngeneration', ['GenerationTime'])

        # Adding unique constraint on 'GenerationTime', fields ['content_type', 'object_id']
        db.create_unique(u'turngeneration_generationtime', ['content_type_id', 'object_id'])

        # Deleting model 'Generator'
        db.delete_table(u'turngeneration_generator')


        # Changing field 'GenerationRule.generator'
        db.alter_column(u'turngeneration_generationrule', 'generator_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['turngeneration.GenerationTime']))

        # Changing field 'Ready.generator'
        db.alter_column(u'turngeneration_ready', 'generator_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['turngeneration.GenerationTime']))

        # Changing field 'Pause.generator'
        db.alter_column(u'turngeneration_pause', 'generator_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['turngeneration.GenerationTime']))

    models = {
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'turngeneration.generationrule': {
            'Meta': {'object_name': 'GenerationRule'},
            'byhour': ('django.db.models.fields.CommaSeparatedIntegerField', [], {'max_length': '64', 'blank': 'True'}),
            'byminute': ('django.db.models.fields.CommaSeparatedIntegerField', [], {'max_length': '64', 'blank': 'True'}),
            'bymonth': ('django.db.models.fields.CommaSeparatedIntegerField', [], {'max_length': '64', 'blank': 'True'}),
            'bymonthday': ('django.db.models.fields.CommaSeparatedIntegerField', [], {'max_length': '64', 'blank': 'True'}),
            'bysetpos': ('django.db.models.fields.CommaSeparatedIntegerField', [], {'max_length': '64', 'blank': 'True'}),
            'byweekday': ('django.db.models.fields.CommaSeparatedIntegerField', [], {'max_length': '64', 'blank': 'True'}),
            'byweekno': ('django.db.models.fields.CommaSeparatedIntegerField', [], {'max_length': '64', 'blank': 'True'}),
            'byyearday': ('django.db.models.fields.CommaSeparatedIntegerField', [], {'max_length': '64', 'blank': 'True'}),
            'count': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'dtstart': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'freq': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '3', 'blank': 'True'}),
            'generator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'rules'", 'to': u"orm['turngeneration.Generator']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'interval': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'until': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
        },
        u'turngeneration.generator': {
            'Meta': {'unique_together': "(('content_type', 'object_id'),)", 'object_name': 'Generator'},
            'allow_pauses': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'autogenerate': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            'generation_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'minimum_between_generations': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'task_id': ('django.db.models.fields.TextField', [], {})
        },
        u'turngeneration.pause': {
            'Meta': {'object_name': 'Pause'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            'generator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'pauses'", 'to': u"orm['turngeneration.Generator']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'reason': ('django.db.models.fields.TextField', [], {}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'turngeneration.ready': {
            'Meta': {'object_name': 'Ready'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            'generator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'readies'", 'to': u"orm['turngeneration.Generator']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {})
        }
    }

    complete_apps = ['turngeneration']
