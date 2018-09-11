# Generated by Django 2.0.7 on 2018-07-30 13:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog_engine', '0002_auto_20180727_1807'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='article',
            field=models.ManyToManyField(related_name='category_article', to='blog_engine.Article'),
        ),
        migrations.AlterField(
            model_name='article',
            name='body',
            field=models.TextField(help_text='Write a main text of article', max_length=250000),
        ),
        migrations.RemoveField(
            model_name='article',
            name='category',
        ),
        migrations.AddField(
            model_name='article',
            name='category',
            field=models.ManyToManyField(related_name='article_category', to='blog_engine.Category'),
        ),
    ]