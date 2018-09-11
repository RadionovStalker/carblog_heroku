import datetime

from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from tinymce.models import HTMLField
from treebeard.mp_tree import MP_Node
from parler.models import TranslatableModel, TranslatedFields
from django.utils.translation import gettext_lazy as _
import os
from django.dispatch import receiver


class TreeCategory(MP_Node):
    name = models.CharField(max_length=30)
    node_order_by = ['name']

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name


# class Category(models.Model):
#     name = models.CharField(max_length=150)
#     article = models.ManyToManyField('Article', related_name='category_article', blank=True)
#     # parent_category = models.ForeignKey('Category',
#     #                                     related_name='cat_parent', blank=True, null=True, on_delete=models.CASCADE)
#     children_category = models.ManyToManyField('Category', related_name='cat_child', blank=True)
#
#     def __str__(self):
#         return self.name
#
#     def get_absolute_url(self):
#         return reverse('category', args=[str(self.id)])
#
#     class Meta:
#         ordering = ['name']

def unique_name_and_path(instance, filename):
    """
    Именование загруженного изображения в вид:
        id_статьи+текущая_дата_в_милисекундах+формат
    """
    upload_to = 'images/articles'
    type_name = filename.split('.')[-1]
    unique_time = str((datetime.datetime.utcnow() - datetime.datetime(1970, 1, 1)).total_seconds() * 1000)
    uni_name = '_'.join([str(instance.id), unique_time])
    filename = '{0}.{1}'.format(uni_name, type_name)
    return os.path.join(upload_to, filename)


class Article(TranslatableModel):

    author = models.ForeignKey(User, related_name="article_author", on_delete=models.CASCADE, help_text="Enter the author of article", default=1)
    date_creation = models.DateTimeField(_('Date of creation'), auto_now_add=True, help_text="Date of creation")
    date_updating = models.DateTimeField(_('Date of updating'), auto_now=True, help_text="Date of update")
    like = models.ManyToManyField(User, _('Like'), blank=True)
    # category = models.ManyToManyField(Category, _('Category'), related_name='article_category')  # убрать и заменить на tree_category или свою структуру
    # image = models.ImageField(_('Image'), upload_to="images/articles", blank=True)
    image = models.ImageField(_('Image'), upload_to=unique_name_and_path, blank=True)

    tree_category = models.ManyToManyField(TreeCategory, _('Category'))

    translations = TranslatedFields(
        title=models.CharField(_('Title'), max_length=250, help_text="Write your name of article"),
        description=models.CharField(_('Description'), max_length=1000,
                                   help_text="Enter a little description of your article"),
        body=HTMLField(),
    )

    def __str__(self):
        return ' '.join([self.title, self.author.username, str(self.date_creation)])

    def __unicode__(self):
        return ' '.join([self.title, self.author.username])

    def get_absolute_url(self):
        return reverse('article-detail', args=[str(self.id)])

    # class Meta:
    #     ordering = ['-date_creation']


class Comment(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    text = models.CharField(max_length=1024, help_text="Write your commentary here")
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_updating = models.DateTimeField(auto_now=True)
    parent_comment = models.ForeignKey('Comment', related_name='com_parent', blank=True, null=True, on_delete=models.CASCADE)
    child_comments = models.ForeignKey('Comment', related_name='com_children', blank=True, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return ' '.join([self.article.title, self.author.username, str(self.date_updating)])

    def get_absolute_url(self):
        return reverse('commentary', args=[str(self.id)])

    class Meta:
        ordering = ['-date_creation', 'author', 'article']


class Gallery(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, default=0, related_name="gallery")
    image = models.ImageField(upload_to="images/gallery", blank=True, null=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.article.title


class Subscribers(models.Model):
    blogger = models.ForeignKey(User, on_delete=models.CASCADE, related_name="subscribers")
    subscriber = models.EmailField()

    class Meta:
        ordering = ['blogger', 'subscriber']

    def __str__(self):
        return ' '.join([self.subscriber, self.blogger.username])


class UserProfile(models.Model):
    image = models.ImageField(blank=True, null=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.user.username


@receiver(models.signals.post_delete, sender=Article)
def del_on_del(sender, instance, **kwargs):
    """
    Удаление изображения из папки /media/ при удалении
    изображения в статье
    """
    if instance.image:
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)


@receiver(models.signals.pre_save, sender=Article)
def del_on_change(sender, instance, **kwargs):
    """
    Удаление изображения из папки /media/ при изменении
    изображения в статье
    """
    if not instance.pk:
        return False
    try:
        old_file = Article.objects.get(pk=instance.pk).image
    except Exception:
        return False
    new_file = instance.image
    if not old_file == new_file:
        try:
            if os.path.isfile(old_file.path):
                os.remove(old_file.path)
        except Exception:
            print("файла, связанного со статьей нет")

