# Generated by Django 2.0.2 on 2018-04-25 13:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0012_auto_20180425_1304'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='detail',
            field=models.CharField(max_length=100, verbose_name='课程描述'),
        ),
    ]