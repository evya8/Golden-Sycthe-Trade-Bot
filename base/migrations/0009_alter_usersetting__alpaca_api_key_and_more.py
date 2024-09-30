# Generated by Django 4.2.14 on 2024-09-08 09:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0008_remove_usersetting_filter_exchange_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usersetting',
            name='_alpaca_api_key',
            field=models.BinaryField(default=b'', max_length=256),
        ),
        migrations.AlterField(
            model_name='usersetting',
            name='_alpaca_api_secret',
            field=models.BinaryField(default=b'', max_length=256),
        ),
        migrations.AlterField(
            model_name='usersetting',
            name='filter_sector',
            field=models.CharField(blank=True, default='', max_length=200, null=True),
        ),
    ]