from django.test import TestCase
from ..models import Article, TreeCategory, Subscribers
from django.contrib.auth.models import User
from django.urls import reverse


class ArticleModelTest(TestCase):

    def create_article(self):
        User.objects.create_user(username='john',
                                 email='jlennon@beatles.com',
                                 password='glass onion')
        TreeCategory.objects.create(name='node', depth=1)
        article = Article()
        article.set_current_language('en')
        article.title = "test title"
        article.description = "test description"
        article.body = "test body"
        article.author = User.objects.get(id=1)
        article.save()
        cat = TreeCategory.objects.get(id=1)
        article.tree_category.add(cat)
        return article.save()

    def test_article(self):
        self.create_article()
        new_art = Article.objects.get(id=1)
        self.assertEqual(new_art.__unicode__(), ' '.join([new_art.title, new_art.author.username]))
        self.assertEqual(new_art.__str__(), ' '.join([new_art.title, new_art.author.username, str(new_art.date_creation)]))
        self.assertEqual(new_art.get_absolute_url(), reverse('article-detail', args=[str(new_art.id)]))


class SubscribersTest(TestCase):

    def create_users_and_subscribe(self):
        author = User.objects.create_user(username='john',
                                 email='jlennon@beatles.com',
                                 password='glass onion')
        subscriber = User.objects.create_user(username='bil',
                                 email='bil@beatles.com',
                                 password='glass onion')
        new_subscribe = Subscribers(blogger=author, subscriber=subscriber.email)
        return new_subscribe.save()

    def test_subscrib(self):
        self.create_users_and_subscribe()
        subs  = Subscribers.objects.get(id=1)
        self.assertEqual(subs.__str__(), "bil@beatles.com john")