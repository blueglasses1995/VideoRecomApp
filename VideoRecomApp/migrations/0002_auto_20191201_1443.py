# Generated by Django 2.2.6 on 2019-12-01 05:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('VideoRecomApp', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='comment',
            name='like_num',
        ),
        migrations.RemoveField(
            model_name='post',
            name='like_num',
        ),
    ]