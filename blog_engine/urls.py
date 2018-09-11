from django.conf.urls import url, include
from . import views
from django.urls import path


urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name="index"),
    url(r'^article/(?P<pk>\d+)$', views.ArticleDetailView.as_view(), name="article-detail"),
    url(r'^author/(?P<pk>\d+)$', views.AuthorDetailView.as_view(), name="author-detail"),
    url(r'^authors/$', views.AuthorListView.as_view(), name="authors"),
    url(r'^profile/(?P<nick>[-\w]+)$', views.UserProfileView.as_view(), name="user-profile"),
    url(r'^register/$', views.RegisterFormView.as_view(), name="registration"),
    url(r'^article_add/$', views.ArticleAddView.as_view(), name="article-add"),
    url(r'article_update/(?P<pk>\d+)$', views.ArticleUpdate.as_view(), name='article-update'),
    url(r'article_delete/(?P<pk>\d+)$', views.UserDeleteArticleView.as_view(), name='article-delete'),
    url(r'profile_update/(?P<pk>\d+)$', views.UserProfileUpdateView.as_view(), name='profile-update'),
]