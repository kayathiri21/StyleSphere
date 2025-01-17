# Generated by Django 5.1.1 on 2024-10-09 09:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clothapp', '0011_order_payment_method_order_payment_status_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='transaction_id',
            new_name='payment_id',
        ),
        migrations.RemoveField(
            model_name='order',
            name='payment_status',
        ),
        migrations.AlterField(
            model_name='order',
            name='payment_method',
            field=models.CharField(choices=[('cod', 'Cash on Delivery'), ('card', 'Credit/Debit Card')], default='cod', max_length=10),
        ),
    ]
