
from carblog.celery import app
from django.core.mail import send_mail
from django.urls import reverse_lazy


@app.task
def send_mail_with_celery(username, host, new_article_pk, emails):
    send_mail('Carblog новая статья от {0}'.format(username),
                          'Автор {0}, на которого Вы подписаны опубликовал новую статью : \n {1}'.format(username,
                                                                                                         "{0}{1}".format(host,
                                                                                                                          reverse_lazy('article-detail', kwargs={"pk": new_article_pk}))),
                          'Carblog', emails)