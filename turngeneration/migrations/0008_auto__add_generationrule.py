# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'GenerationRule'
        db.create_table(u'turngeneration_generationrule', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('generator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['turngeneration.GenerationTime'])),
            ('freq', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=3, blank=True)),
            ('dtstart', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('interval', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
            ('count', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
            ('until', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('bysetpos', self.gf('django.db.models.fields.CommaSeparatedIntegerField')(max_length=64, blank=True)),
            ('bymonth', self.gf('django.db.models.fields.CommaSeparatedIntegerField')(max_length=64, blank=True)),
            ('bymonthday', self.gf('django.db.models.fields.CommaSeparatedIntegerField')(max_length=64, blank=True)),
            ('byyearday', self.gf('django.db.models.fields.CommaSeparatedIntegerField')(max_length=64, blank=True)),
            ('byweekno', self.gf('django.db.models.fields.CommaSeparatedIntegerField')(max_length=64, blank=True)),
            ('byweekday', self.gf('django.db.models.fields.CommaSeparatedIntegerField')(max_length=64, blank=True)),
            ('byhour', self.gf('django.db.models.fields.CommaSeparatedIntegerField')(max_length=64, blank=True)),
            ('byminute', self.gf('django.db.models.fields.CommaSeparatedIntegerField')(max_length=64, blank=True)),
        ))
        db.send_create_signal(u'turngeneration', ['GenerationRule'])


    def backwards(self, orm):
        # Deleting model 'GenerationRule'
        db.delete_table(u'turngeneration_generationrule')


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
            'generator': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['turngeneration.GenerationTime']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'interval': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'until': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
        },
        u'turngeneration.generationtime': {
            'Meta': {'unique_together': "(('content_type', 'object_id'),)", 'object_name': 'GenerationTime'},
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
            'generator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'pauses'", 'to': u"orm['turngeneration.GenerationTime']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'reason': ('django.db.models.fields.TextField', [], {}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'turngeneration.ready': {
            'Meta': {'object_name': 'Ready'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            'generator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'readies'", 'to': u"orm['turngeneration.GenerationTime']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {})
        }
    }

    complete_apps = ['turngeneration']