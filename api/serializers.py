import sys
import os
sys.path.append(os.path.abspath(os.path.pardir))
from blog_engine.models import Article, UserProfile, Gallery, TreeCategory
from rest_framework import serializers
from django.contrib.auth.models import User
from parler_rest.serializers import TranslatableModelSerializer
from parler_rest.fields import TranslatedFieldsField

class Base64ImageField(serializers.ImageField):
    """
    A Django REST framework field for handling image-uploads through raw post data.
    It uses base64 for encoding and decoding the contents of the file.

    Heavily based on
    https://github.com/tomchristie/django-rest-framework/pull/1268

    Updated for Django REST framework 3.
    """

    # def to_internal_value(self, data):
    #     from django.core.files.base import ContentFile
    #     import base64
    #     import six
    #     import uuid
    #
    #     # Check if this is a base64 string
    #     if isinstance(data, six.string_types):
    #         # Check if the base64 string is in the "data:" format
    #         if 'data:' in data and ';base64,' in data:
    #             # Break out the header from the base64 content
    #             header, data = data.split(';base64,')
    #
    #         # Try to decode the file. Return validation error if it fails.
    #         try:
    #             decoded_file = base64.b64decode(data)
    #         except TypeError:
    #             self.fail('invalid_image')
    #
    #         # Generate file name:
    #         file_name = str(uuid.uuid4())[:12] # 12 characters are more than enough.
    #         # Get the file name extension:
    #         file_extension = self.get_file_extension(file_name, decoded_file)
    #
    #         complete_file_name = "%s.%s" % (file_name, file_extension, )
    #
    #         data = ContentFile(decoded_file, name=complete_file_name)
    #
    #     return super(Base64ImageField, self).to_internal_value(data)
    #
    # def get_file_extension(self, file_name, decoded_file):
    #     import imghdr
    #
    #     extension = imghdr.what(file_name, decoded_file)
    #     extension = "jpg" if extension == "jpeg" else extension
    #
    #     return extension


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = [
            'username',
            'last_name',
            'first_name',
            'email',
            # 'url'
        ]
        read_only_fields = ['username']
    # url = serializers.HyperlinkedIdentityField(
    #     view_name='user-detail-api',
    #     lookup_field='pk',
    # )


class UserProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserProfile
        fields = [
            'user',
            'image',
            'url',
        ]
        read_only_fields = ['url', 'image']
        # image = serializers.Field('image.url')
    user = UserSerializer()
    # image = serializers.ImageField(max_length=None, use_url=True)

    url = serializers.HyperlinkedIdentityField(
        view_name='user-detail-api',
        lookup_field='pk',
    )


class GallerySerializer(serializers.ModelSerializer):

    class Meta:
        model = Gallery
        fields = ('image', )
        read_only_fields = ['image']


class TreeCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = TreeCategory
        fields = ('name')


class ArticlePostSerializer(serializers.Serializer):
    tree_category = serializers.IntegerField()
    title = serializers.CharField( max_length=250)
    description = serializers.CharField(max_length=1000)
    body = serializers.CharField()
    language = serializers.CharField(max_length=2, required=False)


class ArticlePutSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField(max_length=250, required=False)
    description = serializers.CharField(max_length=1000, required=False)
    body = serializers.CharField(required=False)
    language = serializers.CharField(max_length=2)


class ArticleDeleteSerializer(serializers.Serializer):
    id = serializers.IntegerField()


class ArticleSerializer(TranslatableModelSerializer):
    translations = TranslatedFieldsField(shared_model=Article)
    class Meta:
        model = Article
        fields = (
            # 'url',
            'id',
            # 'title',
            'author',
            # 'description',
            # 'body',
            'translations',
            'tree_category',
            'image',
            'gallery',
            'likes'
        )
        read_only_fields = ['id', 'url', 'author', 'gallery', 'likes']
    # image = Base64ImageField(max_length=None, use_url=True)
    # url = serializers.HyperlinkedIdentityField(
    #     view_name='article-detail-api',
    #     lookup_field='pk',
    # )
    likes = serializers.SerializerMethodField()

    def get_likes(self, obj):
        return obj.like.count()

    author = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field='username')
    gallery = GallerySerializer(many=True)
