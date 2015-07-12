# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('drug_search', '0005_version5'),
    ]

    operations = [
        migrations.DeleteModel(
            name='GeneCategory',
        ),
        migrations.AlterField(
            model_name='gene',
            name='category',
            field=models.ManyToManyField(to='drug_search.Group'),
        ),
    ]
