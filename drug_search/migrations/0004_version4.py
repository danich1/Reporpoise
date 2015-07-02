# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('drug_search', '0003_test'),
    ]

    operations = [
        migrations.CreateModel(
            name='GeneCategory',
            fields=[
                ('category', models.CharField(default=b'unknown', max_length=100, serialize=False, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='Source',
            fields=[
                ('source', models.CharField(default=b'unknown', max_length=100, serialize=False, primary_key=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='interactions',
            name='source',
        ),
        migrations.AddField(
            model_name='gene',
            name='category',
            field=models.ManyToManyField(to='drug_search.GeneCategory'),
        ),
        migrations.AddField(
            model_name='interactions',
            name='source',
            field=models.ManyToManyField(to='drug_search.Source'),
        ),
    ]
