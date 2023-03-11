# Generated by Django 2.2.16 on 2023-03-04 15:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0003_auto_20230304_1620'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='is_favorited',
            field=models.BooleanField(null=True, verbose_name='Есть в избранном'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='is_in_shopping_cart',
            field=models.BooleanField(null=True, verbose_name='Есть в корзине'),
        ),
    ]
