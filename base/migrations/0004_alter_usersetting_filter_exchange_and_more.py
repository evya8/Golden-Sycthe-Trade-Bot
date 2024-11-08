# Generated by Django 4.2.14 on 2024-08-08 08:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0003_alter_usersetting_filter_exchange'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usersetting',
            name='filter_exchange',
            field=models.CharField(blank=True, default='', max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='usersetting',
            name='filter_sector',
            field=models.CharField(blank=True, default='', max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='usersetting',
            name='filter_type',
            field=models.CharField(blank=True, default='both', max_length=20, null=True),
        ),
    ]
