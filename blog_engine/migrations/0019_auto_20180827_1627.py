# Generated by Django 2.1 on 2018-08-27 13:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog_engine', '0018_remove_category_parent_category'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='category',
            name='children_category',
        ),
        migrations.AddField(
            model_name='category',
            name='children_category',
            field=models.ManyToManyField(blank=True, related_name='cat_child', to='blog_engine.Category'),
        ),
    ]