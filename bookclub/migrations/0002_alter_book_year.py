# Generated by Django 3.2.11 on 2022-01-27 14:38

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookclub', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='year',
            field=models.PositiveIntegerField(blank=True, default=2022, validators=[django.core.validators.MaxValueValidator(2022), django.core.validators.MinValueValidator(1)]),
        ),
    ]
