# Generated by Django 3.1.4 on 2022-07-09 14:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('App', '0003_cart_order'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='order_times',
            new_name='order_items',
        ),
    ]
