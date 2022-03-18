# Generated by Django 3.2.11 on 2022-03-17 14:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bookclub', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='club',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='events', to='bookclub.club'),
        ),
    ]
