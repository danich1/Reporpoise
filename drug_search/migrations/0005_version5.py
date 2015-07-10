# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('drug_search', '0004_version4'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='gene',
            name='name',
        ),
        migrations.RemoveField(
            model_name='gene',
            name='uniprot_id',
        ),
    ]
