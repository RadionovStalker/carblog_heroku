from django.contrib import admin
from .models import *
from treebeard.admin import TreeAdmin
from treebeard.forms import movenodeform_factory
from parler.admin import TranslatableAdmin


class MyAdmin(TreeAdmin):
    fields = ('name', '_position', '_ref_node_id',)
    form = movenodeform_factory(TreeCategory)


admin.site.register(TreeCategory, MyAdmin)


@admin.register(Gallery)
class GalleryAdmin(admin.ModelAdmin):
    pass


@admin.register(Subscribers)
class SubscribersAdmin(admin.ModelAdmin):
    pass


class GalleryInline(admin.TabularInline):
    model = Gallery
    extra = 0


class ArticleInline(admin.TabularInline):
    model = Article
    extra = 0


class UserInline(admin.TabularInline):
    model = User
    extra = 0


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0


class SubscribersInline(admin.TabularInline):
    model = Subscribers
    extra = 0


@admin.register(Article)
class ArticleAdmin(TranslatableAdmin):
    inlines = [CommentInline, GalleryInline]


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    pass


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    pass

