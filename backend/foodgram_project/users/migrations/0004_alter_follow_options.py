# Generated by Django 3.2.18 on 2023-03-18 05:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_auto_20230311_2003'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='follow',
            options={'ordering': ('user', 'author'), 'verbose_name': 'Подписки'},
        ),
    ]
