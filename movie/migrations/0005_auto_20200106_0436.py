# Generated by Django 2.2.6 on 2020-01-05 20:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('movie', '0004_auto_20200106_0434'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='FriendFavourite',
            new_name='ProfileFavourite',
        ),
    ]
