# Generated by Django 3.0.7 on 2020-07-06 09:08

import book.models
import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('book', '0008_auto_20200705_2022'),
    ]

    operations = [
        migrations.AlterField(
            model_name='waiting',
            name='add_time',
            field=models.TimeField(default=datetime.time(14, 38, 11, 495484)),
        ),
        migrations.AlterField(
            model_name='waiting',
            name='no_people',
            field=models.IntegerField(validators=[book.models.capacity_validation]),
        ),
    ]
