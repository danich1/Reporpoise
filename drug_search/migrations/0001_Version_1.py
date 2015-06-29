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
                ('uniprot_id', models.CharField(default=b'unknown', max_length=100)),
                ('name', models.CharField(default=b'unknown', max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('name', models.CharField(max_length=100, serialize=False, primary_key=True)),
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
