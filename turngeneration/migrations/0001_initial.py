# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'GenerationTime'
        db.create_table(u'turngeneration_generationtime', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('generation_time', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('task_id', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'turngeneration', ['GenerationTime'])

        # Adding unique constraint on 'GenerationTime', fields ['content_type', 'object_id']
        db.create_unique(u'turngeneration_generationtime', ['content_type_id', 'object_id'])

        # Adding model 'GenerationRule'
        db.create_table(u'turngeneration_generationrule', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('generator', self.gf('django.db.models.fields.related.ForeignKey')(related_name='rules', to=orm['turngeneration.GenerationTime'])),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('at_least', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
            ('weekday', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
            ('date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('time', self.gf('django.db.models.fields.TimeField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'turngeneration', ['GenerationRule'])


    def backwards(self, orm):
        # Removing unique constraint on 'GenerationTime', fields ['content_type', 'object_id']
        db.delete_unique(u'turngeneration_generationtime', ['content_type_id', 'object_id'])

        # Deleting model 'GenerationTime'
        db.delete_table(u'turngeneration_generationtime')

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
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'at_least': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'generator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'rules'", 'to': u"orm['turngeneration.GenerationTime']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'time': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'weekday': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        u'turngeneration.generationtime': {
            'Meta': {'unique_together': "(('content_type', 'object_id'),)", 'object_name': 'GenerationTime'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            'generation_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'task_id': ('django.db.models.fields.TextField', [], {})
        }
    }

    complete_apps = ['turngeneration']