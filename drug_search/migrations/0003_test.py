# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('drug_search', '0002_Version2'),
    ]

    operations = [
        migrations.CreateModel(
            name='Interactions',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('source', models.CharField(max_length=200)),
                ('gene_source', models.ForeignKey(to='drug_search.Gene')),
                ('gene_target', models.ForeignKey(related_name='gene_targets', to='drug_search.Gene')),
            ],
        ),
        migrations.AddField(
            model_name='gene',
            name='interact',
            field=models.ManyToManyField(to='drug_search.Gene', through='drug_search.Interactions'),
        ),
    ]
