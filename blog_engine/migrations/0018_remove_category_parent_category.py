# Generated by Django 2.1 on 2018-08-27 13:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog_engine', '0017_auto_20180827_1600'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='category',
            name='parent_category',
        ),
    ]