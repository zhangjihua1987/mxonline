# Generated by Django 2.0.2 on 2018-04-25 13:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0013_auto_20180425_1310'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='detail',
            field=models.TextField(verbose_name='课程详情'),
        ),
    ]
