# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('drug_search', '0001_Version_1'),
    ]

    operations = [
        migrations.CreateModel(
            name='Phenotype',
            fields=[
                ('name', models.CharField(max_length=400, serialize=False, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='PhenotypeMap',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('z_score', models.FloatField()),
                ('gene', models.ForeignKey(to='drug_search.Gene')),
                ('phenotype', models.ForeignKey(to='drug_search.Phenotype')),
            ],
        ),
        migrations.CreateModel(
            name='Word',
            fields=[
                ('label', models.CharField(max_length=200, serialize=False, primary_key=True)),
                ('count', models.IntegerField()),
                ('drug', models.ManyToManyField(to='drug_search.Drug')),
            ],
        ),
        migrations.AddField(
            model_name='phenotype',
            name='gene',
            field=models.ManyToManyField(to='drug_search.Gene', through='drug_search.PhenotypeMap'),
        ),
    ]
