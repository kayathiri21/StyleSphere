# Generated by Django 5.1.1 on 2024-09-26 09:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clothapp', '0002_product'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='is_in_stock',
            field=models.BooleanField(default=True),
        ),
    ]