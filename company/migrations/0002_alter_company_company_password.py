# Generated by Django 3.2.17 on 2023-03-10 07:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='company',
            name='company_password',
            field=models.CharField(max_length=255),
        ),
    ]
