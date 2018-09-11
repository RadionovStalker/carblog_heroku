import sys
import os
sys.path.append(os.path.abspath(os.path.pardir))
from .serializers import ArticleSerializer, UserProfileSerializer, ArticlePostSerializer, ArticlePutSerializer, \
    ArticleDeleteSerializer
from rest_framework import generics
from blog_engine.models import Article, UserProfile, TreeCategory
from rest_framework.response import Response
from rest_framework.reverse import reverse
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework import status
from rest_framework import permissions
from django.utils import translation
from django.conf import settings


class ArticleListAPI(generics.ListAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    name = 'article-list-api'


class ArticleLikeAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]
    name = "article-like-api"

    def post(self, request, **kwargs):
        try:
            print(kwargs)
            id = ArticleDeleteSerializer(data=kwargs)
            if id.is_valid():
                art = Article.objects.get(id=id.data.get('id'))
                if art.author != request.user:
                    return Response({"message": "Forbidden"}, status=403)
                if request.user in art.like.all():
                    art.like.remove(request.user)
                    return Response("Delete from favourite", status=200)
                else:
                    art.like.add(self.request.user)
                    return Response("Add to favourite", status=200)
            else:
                raise Exception("Invalid value of id")
        except Exception as error:
            return Response({"message": repr(error)}, status=400)


class ArticleDetailAPI(APIView):
    # queryset = Article.objects.all()
    # serializer_class = ArticleSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, ]
    name = 'article-detail-api'

    def get(self, request):
        """curl http://127.0.0.1:8000/ru/api/article/?id=20"""
        try:
            article = Article.objects.filter(id=request.GET.get('id'))
            if not article:
                raise Exception("No article with id={0}".format(request.GET.get('id')))
            serializer = ArticleSerializer(article, many=True)
            return Response({"data": serializer.data})
        except Exception as error:
            return Response({"message": repr(error)}, status=400)

    # добавить рассылку подписчикам
    def post(self, request):
        """>curl -X POST -H "Content-Type: application/json" -d "{\"title\":\"api\",\"description\":\"api\",\"body\":\"api\",\"tree_category\":\"1\",\"language\":\"en\"}" -u admin:qwerty12345  http://127.0.0.1:8000/ru
/api/article/
"""
        try:
            print(request)
            new_article = ArticlePostSerializer(data=request.data)
            print(new_article)
            if new_article.is_valid():
                print(settings.LANGUAGES)
                if 'language' in new_article.data.keys():
                    lang = new_article.data['language']
                    for lang_code, lang_name in settings.LANGUAGES:
                        if lang_code == lang:
                            print('yes')
                            break
                    else:
                        raise Exception("Invalid language")
                else:
                    # print(settings.PARLER_LANGUAGES['default']['fallbacks'][0])
                    lang = settings.PARLER_LANGUAGES['default']['fallbacks'][0]
                # print(lang)
                # print("valid")
                # print(new_article)
                title = new_article.data.get('title')
                desc = new_article.data.get('description')
                body = new_article.data.get('body')
                cat = new_article.data.get('tree_category')
                # print(title)
                # print(desc)
                # print(body)
                # print(cat)
                # print(request.user)
                art = Article()
                art.set_current_language(lang)
                art.title = title
                art.description = desc
                art.body = body
                art.author = request.user
                art.save()
                # так добавляется поле manyTomanyField
                cat = TreeCategory.objects.get(id=cat)
                art.tree_category.add(cat)
                art.save()
                # serializer = ArticleSerializer(art, many=True)
                # print(serializer.data)
                return Response({"message": "Successfully added"}, status=200)
            else:
                print("invalid")
                raise Exception("Invalid argument")
        except Exception as error:
            return Response({"message": repr(error)}, status=400)

    def put(self, request):
        """>curl -X PUT -H "Content-Type: application/json" -d "{\"id\":\"20\",\"title\":\"api update\",\"description\":\"api update\",\"body\":\"api update\",\"language\":\"en\"}" -u admin:qwerty12345  http://127.0.0
.1:8000/ru/api/article/
"""
        try:
            data_for_art = ArticlePutSerializer(data=request.data)
            if data_for_art.is_valid():
                print("valid")
                if 'id' in data_for_art.data.keys():
                    art_for_upd = Article.objects.get(id=data_for_art.data.get('id'))
                    if art_for_upd:
                        if art_for_upd.author != request.user:
                            return Response({"message":"Forbidden"}, status=403)
                    else:
                        return Response({"message":"No article with id={0}".format(data_for_art.data.get('id'))}, status=404)
                        # raise Exception("No article with id={0}".format(data_for_art.data.get('id')))
                else:
                    raise Exception("id is necessary parameter")
                if 'language' in data_for_art.data.keys():
                    lang = data_for_art.data['language']
                    for lang_code, lang_name in settings.LANGUAGES:
                        if lang_code == lang:
                            break
                    else:
                        raise Exception("Invalid language")
                else:
                    raise Exception("Language is necessary parameter")
                art_for_upd.set_current_language(lang)
                # print(lang)
                # print(art_for_upd.title)
                # print(data_for_art.data.keys())
                if 'title' in data_for_art.data.keys():
                    print(1)
                    art_for_upd.title = data_for_art.data.get('title')
                elif not art_for_upd.title:
                    print(2)
                    raise Exception("Field 'title' is null, you must put parameter 'title'")
                if 'description' in data_for_art.data.keys():
                    art_for_upd.description = data_for_art.data.get('description')
                elif not art_for_upd.description:
                    raise Exception("Field 'description' is null, you must put parameter 'description'")
                if 'body' in data_for_art.data.keys():
                    art_for_upd.body = data_for_art.data.get('body')
                elif not art_for_upd.body:
                    raise Exception("Field 'body' is null, you must put parameter 'body'")
                art_for_upd.save()
                return Response({"message": "Successfully updated"}, status=200)
            else:
                raise Exception("Invalid argument")
        except Exception as error:
            return Response({"message": repr(error)}, status=400)

    def delete(self, request):
        try:
            id = ArticleDeleteSerializer(data=request.data)
            if id.is_valid():
                if 'id' in id.data.keys():
                    art_for_del = Article.objects.get(id=id.data.get('id'))
                    if art_for_del:
                        if art_for_del.author != request.user:
                            return Response({"message": "Forbidden"}, status=403)
                    else:
                        return Response({"message": "No article with id={0}".format(art_for_del.data.get('id'))},
                                        status=404)
                else:
                    raise Exception("id is necessary parameter")
                art_for_del.delete()
                return Response({"message": "Successfully deleted"}, status=200)
            else:
                raise Exception("Invalid value of id")
        except Exception as error:
            return Response({"message": repr(error)}, status=400)


class UserProfileDetailAPI(generics.RetrieveAPIView):
    lookup_field = 'pk'
    name = 'user-detail-api'
    serializer_class = UserProfileSerializer
    queryset = UserProfile.objects.all()


class UserProfileListAPI(generics.ListAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    name = 'user-list-api'


class ApiRoot(generics.GenericAPIView):
    name = 'api-root'
    queryset = Article.objects.all()

    def get(self, request):
        return Response({
            'articles': reverse(ArtilceListAPI.name, request=request),
            'authors': reverse(UserProfileListAPI.name, request=request)
        })
