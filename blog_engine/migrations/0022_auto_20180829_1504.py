# Generated by Django 2.1 on 2018-08-29 12:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('blog_engine', '0021_article_tree_category'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='comment',
            options={'ordering': ['-date_creation', 'author', 'article']},
        ),
        migrations.AlterField(
            model_name='gallery',
            name='article',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='blog_engine.Article'),
        ),
        migrations.AlterField(
            model_name='gallery',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='images/articles'),
        ),
    ]