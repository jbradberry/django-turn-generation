# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Pause'
        db.create_table(u'turngeneration_pause', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('generator', self.gf('django.db.models.fields.related.ForeignKey')(related_name='pauses', to=orm['turngeneration.GenerationTime'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='turngeneration_pauses', to=orm['auth.User'])),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')()),
            ('reason', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'turngeneration', ['Pause'])


    def backwards(self, orm):
        # Deleting model 'Pause'
        db.delete_table(u'turngeneration_pause')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
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
            'generator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'pauses'", 'to': u"orm['turngeneration.GenerationTime']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reason': ('django.db.models.fields.TextField', [], {}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'turngeneration_pauses'", 'to': u"orm['auth.User']"})
        }
    }

    complete_apps = ['turngeneration']