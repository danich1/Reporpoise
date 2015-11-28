# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Drug',
            fields=[
                ('name', models.CharField(max_length=300, serialize=False, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='DrugID',
            fields=[
                ('drug_id', models.CharField(max_length=100, serialize=False, primary_key=True)),
                ('name', models.ForeignKey(to='drug_search.Drug')),
            ],
        ),
        migrations.CreateModel(
            name='Gene',
            fields=[
                ('gene_name', models.CharField(default=b'unknown', max_length=100, serialize=False, primary_key=True)),
                ('gene_id', models.CharField(default=b'unknown', max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='GeneScoreSource',
            fields=[
                ('source', models.CharField(default=b'unknown', max_length=100, serialize=False, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('name', models.CharField(max_length=100, serialize=False, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='Interactions',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('gene_source', models.ForeignKey(to='drug_search.Gene')),
                ('gene_target', models.ForeignKey(related_name='gene_targets', to='drug_search.Gene')),
            ],
        ),
        migrations.CreateModel(
            name='InteractionSource',
            fields=[
                ('source', models.CharField(default=b'unknown', max_length=100, serialize=False, primary_key=True)),
            ],
        ),
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
                ('p_val', models.FloatField()),
                ('log_score', models.FloatField()),
                ('gene', models.ForeignKey(to='drug_search.Gene')),
                ('phenotype', models.ForeignKey(to='drug_search.Phenotype')),
                ('source', models.ForeignKey(to='drug_search.GeneScoreSource')),
            ],
        ),
        migrations.CreateModel(
            name='Targets',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('action', models.CharField(max_length=300)),
                ('drug', models.ForeignKey(to='drug_search.Drug')),
                ('gene', models.ForeignKey(to='drug_search.Gene')),
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
        migrations.AddField(
            model_name='interactions',
            name='source',
            field=models.ManyToManyField(to='drug_search.InteractionSource'),
        ),
        migrations.AddField(
            model_name='gene',
            name='category',
            field=models.ManyToManyField(to='drug_search.Group'),
        ),
        migrations.AddField(
            model_name='gene',
            name='interact',
            field=models.ManyToManyField(to='drug_search.Gene', through='drug_search.Interactions'),
        ),
        migrations.AddField(
            model_name='drug',
            name='group',
            field=models.ManyToManyField(to='drug_search.Group'),
        ),
        migrations.AddField(
            model_name='drug',
            name='target',
            field=models.ManyToManyField(to='drug_search.Gene', through='drug_search.Targets'),
        ),
    ]
