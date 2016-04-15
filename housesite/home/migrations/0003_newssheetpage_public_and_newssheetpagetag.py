# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-15 06:03
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import modelcluster.contrib.taggit
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('taggit', '0002_auto_20150616_2121'),
        ('home', '0002_newssheetindexpage_newssheetpage_newssheetpageattachments'),
    ]

    operations = [
        migrations.CreateModel(
            name='NewssheetPageTag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='newssheetpage',
            name='public',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='newssheetpagetag',
            name='content_object',
            field=modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='tagged_items', to='home.NewssheetPage'),
        ),
        migrations.AddField(
            model_name='newssheetpagetag',
            name='tag',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='home_newssheetpagetag_items', to='taggit.Tag'),
        ),
        migrations.AddField(
            model_name='newssheetpage',
            name='tags',
            field=modelcluster.contrib.taggit.ClusterTaggableManager(blank=True, help_text='A comma-separated list of tags.', through='home.NewssheetPageTag', to='taggit.Tag', verbose_name='Tags'),
        ),
    ]
