# Generated by Django 2.0.7 on 2018-08-05 11:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog_engine', '0007_auto_20180805_1413'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='image',
            field=models.ImageField(blank=True, upload_to='images/articles'),
        ),
    ]