# Generated by Django 4.2.14 on 2024-07-21 07:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0002_botoperation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usersetting',
            name='position_size',
            field=models.FloatField(help_text='Percentage of equity to allocate to each position'),
        ),
    ]
