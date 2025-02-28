# Generated by Django 5.0.7 on 2024-08-04 13:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pilotlog', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attribute',
            name='name',
            field=models.CharField(db_index=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='childattribute',
            name='name',
            field=models.CharField(blank=True, db_index=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='row',
            name='table',
            field=models.CharField(db_index=True, max_length=64, null=True),
        ),
        migrations.AddIndex(
            model_name='attributevalue',
            index=models.Index(fields=['row', 'attribute'], name='pilotlog_at_row_id_eb2aa2_idx'),
        ),
        migrations.AddIndex(
            model_name='attributevalue',
            index=models.Index(fields=['row', 'child_attribute'], name='pilotlog_at_row_id_c319f6_idx'),
        ),
    ]
