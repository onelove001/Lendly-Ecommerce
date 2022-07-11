# Generated by Django 3.1.4 on 2022-07-09 09:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('App', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='detailed_text',
            field=models.TextField(max_length=500, verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='product',
            name='preview_text',
            field=models.TextField(max_length=100, verbose_name='Preview Text'),
        ),
    ]
