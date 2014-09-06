# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Pause.user'
        db.delete_column(u'turngeneration_pause', 'user_id')

        # Adding field 'Pause.content_type'
        db.add_column(u'turngeneration_pause', 'content_type',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=0, to=orm['contenttypes.ContentType']),
                      keep_default=False)

        # Adding field 'Pause.object_id'
        db.add_column(u'turngeneration_pause', 'object_id',
                      self.gf('django.db.models.fields.PositiveIntegerField')(default=0),
                      keep_default=False)


    def backwards(self, orm):

        # User chose to not deal with backwards NULL issues for 'Pause.user'
        raise RuntimeError("Cannot reverse this migration. 'Pause.user' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration        # Adding field 'Pause.user'
        db.add_column(u'turngeneration_pause', 'user',
                      self.gf('django.db.models.fields.related.ForeignKey')(related_name='turngeneration_pauses', to=orm['auth.User']),
                      keep_default=False)

        # Deleting field 'Pause.content_type'
        db.delete_column(u'turngeneration_pause', 'content_type_id')

        # Deleting field 'Pause.object_id'
        db.delete_column(u'turngeneration_pause', 'object_id')


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
        },
        u'turngeneration.pause': {
            'Meta': {'object_name': 'Pause'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            'generator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'pauses'", 'to': u"orm['turngeneration.GenerationTime']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'reason': ('django.db.models.fields.TextField', [], {}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {})
        }
    }

    complete_apps = ['turngeneration']