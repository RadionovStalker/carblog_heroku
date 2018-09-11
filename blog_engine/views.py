from django.db.models import Count
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from .models import *
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.views.generic.edit import FormView, UpdateView, DeleteView
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile
from .forms import UpdateProfileFormView
from .forms import AddNewArticle, CHOICE_LIST, UpdateArticleForm
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from parler.views import TranslatableSlugMixin
from django.http import JsonResponse
from django.core.mail import send_mail
from django.utils.translation import get_language
from django.utils.http import is_safe_url, urlunquote
from django.contrib.auth.mixins import LoginRequiredMixin
from .tasks import send_mail_with_celery


# def get_next_url(request):
#     next = request.META.get('HTTP_REFERER')
#     if next:
#         next = urlunquote(next)  # HTTP_REFERER may be encoded.
#     if not is_safe_url(url=next, host=request.get_host()):
#         next = '/'
#     return next


class IndexView(generic.ListView):
    model = Article
    template_name = 'index.html'
    paginate_by = 3

    def post(self, request, *args, **kwargs):
        print('post before')
        print(self.request.POST)
        if 'unfilter_btn' in self.request.POST:
            print("delete filters")
            self.request.session['order_by'] = '-date_creation'
            self.request.session['group_by'] = 'no'
        else:
            self.request.session['order_by'] = self.request.POST.get('order_by', '-date_creation')
            self.request.session['group_by'] = self.request.POST.getlist('group_by', 'no')
        print('post after')
        print(self.request.POST)
        # print(self.request.session['group_by'])
        return super().get(request, *args, **kwargs)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order_by'] = self.request.session.get('order_by', '-date_creation')
        context['order_choice'] = CHOICE_LIST
        print("context")
        cat_names = list()
        for cat in TreeCategory.objects.all():
            cat_names.append(cat.name)
        context['group_choice'] = cat_names
        print(context['group_choice'])
        context['group_by'] = self.request.session.get('group_by', 'no')
        print(context['group_by'])
        # print('context')
        # print(context)
        return context

    def get_queryset(self):
        print("queryset")
        print(self.request.session)
        grouping = self.request.session.get('group_by', 'no')
        print("it is grouping:")
        print(grouping)
        if grouping != 'no':
            categories = TreeCategory.objects.filter(name__in=grouping)
            names_cat = list()
            for cat in categories:
                sub_categories = TreeCategory.get_tree(cat)
                for sub_cat in sub_categories:
                    if sub_cat.name not in names_cat:
                        names_cat.append(sub_cat.name)
            print(names_cat)
            objects = Article.objects.filter(tree_category__name__in=names_cat,  translations__language_code=get_language())
        else:
            objects = Article.objects.filter(translations__language_code=get_language())

        ordering = self.request.session.get('order_by', '-date_creation')
        if ordering == 'like':
            return objects.annotate(q_count=Count('like')).order_by('q_count', '-date_creation')
        elif ordering == '-like':
            return objects.annotate(q_count=Count('like')).order_by('q_count', 'date_creation').reverse()
        else:
            return objects.order_by(ordering)


class ArticleDetailView(generic.DetailView):
    model = Article

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        article = get_object_or_404(Article, pk=self.kwargs['pk'])
        context['gallery'] = Gallery.objects.filter(article=article)
        context['like_count'] = article.like.count()
        if self.request.user in article.like.all():
            context['liked'] = "Unlike"
        else:
            context['liked'] = "Like"
        comments = Comment.objects.filter(article=article)
        if comments:
            context['comments'] = comments
            context['com_count'] = len(comments)
        else:
            context['comments'] = 'none'
            context['com_count'] = 0

        return context

    def get(self, request, *args, **kwargs):
        article = get_object_or_404(Article, pk=self.kwargs['pk'])
        print("get like")
        print(request.GET)
        data = dict()
        if 'type' in request.GET:
            if request.GET['type'] == 'like':
                if self.request.user in article.like.all():
                    article.like.remove(self.request.user)
                    data['liked'] = 1
                else:
                    data['liked'] = 2
                    article.like.add(self.request.user)
                data['count_like'] = article.like.count()
                return JsonResponse(data)
                # return super(ArticleDetailView, self).get(request, *args, **kwargs)
        return super(ArticleDetailView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        article = Article.objects.get(pk=self.kwargs['pk'])
        print(request.POST)
        if 'com_text' in request.POST:
            new_comment = Comment(article=article, text=request.POST['com_text'], author=request.user) # добавить ручную проверку на безопасность вводимого текста
            new_comment.save()
            return redirect("article-detail", pk=self.kwargs['pk'])
        elif 'ans_text' in request.POST:
            parent_comment = Comment.objects.get(id=request.POST['coment_id'])
            new_comment = Comment(article=article, text=request.POST['ans_text'], author=request.user, parent_comment=parent_comment)
            new_comment.save()
            parent_comment.child_comments = new_comment
            parent_comment.save()
            return redirect("article-detail", pk=self.kwargs['pk'])
        elif 'update_com' in request.POST:
            comment_to_up = Comment.objects.get(id=request.POST['coment_id'])
            comment_to_up.text = request.POST['upd_com_text']
            comment_to_up.save()
            return redirect("article-detail", pk=self.kwargs['pk'])
        elif 'delete_com' in request.POST:
            Comment.objects.get(id=int(request.POST['coment_id'])).delete()
            return redirect("article-detail", pk=self.kwargs['pk'])
        else:
            return redirect("article-detail", pk=self.kwargs['pk'])


class AuthorDetailView(generic.DetailView):
    model = User
    template_name = 'blog_engine/user_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        author = get_object_or_404(User, pk=self.kwargs['pk'])
        context['articles'] = Article.objects.filter(author=author)
        user = UserProfile.objects.get(pk=author.pk)
        context['avatar'] = user.image
        if self.request.user.is_authenticated:
            subscribs = Subscribers.objects.filter(subscriber=self.request.user.email)
            print(subscribs)
            for subs in subscribs:
                if author == subs.blogger:
                    context['subscribed'] = "Отменить подписку"
                    break
            else:
                context['subscribed'] = "Подписаться"
        context['count_subs'] = author.subscribers.all().count()
        return context

    def get(self, request, *args, **kwargs):
        blogger = get_object_or_404(User, pk=self.kwargs['pk'])
        print("subscribe")
        print(request.GET)
        data = dict()
        if 'action' in request.GET:
            if request.GET['action'] == 'subscribe':
                subscribs = Subscribers.objects.filter(subscriber=self.request.user.email)
                for subs in subscribs:
                    if blogger == subs.blogger:
                        subs.delete()
                        data['subscribed'] = 1
                        break
                else:
                    new_subscribe = Subscribers(blogger=blogger, subscriber=self.request.user.email)
                    data['subscribed'] = 2
                    new_subscribe.save()
                data['count_subs'] = blogger.subscribers.all().count()
                return JsonResponse(data)
        return super(AuthorDetailView, self).get(request, *args, **kwargs)


class AuthorListView(generic.ListView):
    model = User
    template_name = 'blog_engine/authors_list.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        auth_art = dict()
        for author in User.objects.all():
            auth_art[author] = Article.objects.filter(author=author).count()
        context['count'] = auth_art
        return context


class ArticleAddView(FormView):
    form_class = AddNewArticle
    template_name = 'blog_engine/add_article.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        new_article = form.save()
        subscribs = Subscribers.objects.filter(blogger=self.request.user)
        emails = list()
        for subs in subscribs:
            emails.append(subs.subscriber)
        if len(emails) > 0:
            send_mail_with_celery.delay(self.request.user.username, self.request.get_host(), new_article.pk, emails)
            # send_mail('Carblog новая статья от {0}'.format(self.request.user.username),
            #           'Автор {0}, на которого Вы подписаны опубликовал новую статью : \n {1}'.format(self.request.user.username,
            #                                                                                          "{0}{1}".format(self.request.get_host(),
            #                                                                                                           reverse_lazy('article-detail', kwargs={"pk": new_article.pk}))),
            #           'Carblog', emails)
        for item in self.request.FILES.getlist('gallery'):
            Gallery.objects.create(image=item, article=new_article)
        self.success_url = reverse_lazy('article-detail', kwargs={"pk": new_article.pk})
        return super(ArticleAddView, self).form_valid(form)


class ArticleUpdate(UpdateView):
    model = Article
    form_class = UpdateArticleForm
    template_name = 'blog_engine/update_article.html'

    # доработанная функция
    def is_current_user(self):
        try:
            article = get_object_or_404(Article, pk=int(self.kwargs['pk']))
            author = article.author
            return self.request.user == author
        except():
            print("Нет пользователя с данным pk")


class UserProfileView(generic.TemplateView):
    # form_class = UpdateProfileFormView
    template_name = 'blog_engine/user_profile.html'
    success_url = "/"
    # paginate_by = 5

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.kwargs['nick'] == self.request.user.username:
            user_id = User.objects.get(username=self.kwargs['nick'])
            user = UserProfile.objects.get(pk=user_id.pk)
            context['user_co'] = user_id
            context['avatar'] = user.image
            is_user = True

            # пример пагинатора статей
            articles = Article.objects.filter(author=user_id)
            paginator = Paginator(articles, 5)  # Show 5 items per page
            page = self.request.GET.get('page')
            context['articles'] = paginator.get_page(page)

            liked_art = Article.objects.filter(like=user_id)
            paginator_like = Paginator(liked_art, 5)
            page = self.request.GET.get('page')
            context['liked_art'] = paginator_like.get_page(page)

        else:
            is_user = False
        context['is_user'] = is_user
        return context


class UserProfileUpdateView(FormView):
    form_class = UpdateProfileFormView
    template_name = 'blog_engine/update_profile.html'

    def get_initial(self):
        user = User.objects.get(pk=self.kwargs['pk'])
        user_image = UserProfile.objects.get(pk=user.pk)
        return {'last_name': user.last_name,
                'first_name': user.first_name,
                'email': user.email,
                'password': user.password,
                'image': user_image.image}

    def form_valid(self, form):
        lastname = form.cleaned_data['last_name']
        firstname = form.cleaned_data['first_name']
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']
        image = form.cleaned_data['image']
        user = User.objects.get(pk=self.kwargs['pk'])
        user.last_name = lastname
        user.first_name = firstname
        user.email = email
        user.password = password
        user.save()
        user_image = UserProfile.objects.get(pk=user.pk)
        user_image.image = image
        user_image.save()

        return super(UserProfileUpdateView, self).form_valid(form)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        if int(self.kwargs['pk']) == self.request.user.pk:
            user = User.objects.get(pk = self.kwargs['pk'])
            context['user_co'] = user
            user_img = UserProfile.objects.get(pk=user.pk)
            context['avatar'] = user_img.image
            is_user = True
        else:
            is_user = False
        context['is_user'] = is_user
        return context

    def get_success_url(self):
        return reverse('user-profile', kwargs={"nick" : self.request.user.username})


class UserDeleteArticleView(DeleteView):

    model = Article
    # success_url = reverse_lazy('user-profile/','paradox')  # как возвращать на профиль этого же автора?
    template_name = 'blog_engine/article_delete.html'

    def get_success_url(self):
        return reverse('user-profile', kwargs={"nick" : self.object.author.username})


class RegisterFormView(FormView):
    form_class = UserCreationForm

    # Ссылка, на которую будет перенаправляться пользователь в случае успешной регистрации.
    success_url = "/accounts/login"

    # Шаблон, который будет использоваться при отображении представления.
    template_name = "register.html"

    def form_valid(self, form):
        # Создаём пользователя, если данные в форму были введены корректно.
        user = form.save()
        user_profile = UserProfile(user=user)
        user_profile.save()

        # Вызываем метод базового класса
        return super(RegisterFormView, self).form_valid(form)



