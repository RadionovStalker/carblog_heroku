from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.ApiRoot.as_view(), name='api-root'),
    url(r'^articles/$', views.ArticleListAPI.as_view(), name='article-list-api'),
    url(r'^article/$', views.ArticleDetailAPI.as_view(), name='article-detail-api'),
    url(r'^user/(?P<pk>\d+)$', views.UserProfileDetailAPI.as_view(), name="user-detail-api"),
    url(r'^users/$', views.UserProfileListAPI.as_view(), name="user-list-api"),
    url(r'^article/like/(?P<id>\d+)$', views.ArticleLikeAPI.as_view(), name="article-like-api"),
]
