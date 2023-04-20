from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.contrib.sites.models import Site
from django.utils.timezone import datetime
from django.conf import settings
from datetime import timedelta
from .models import Post, Category


@shared_task
def notify_subscribers(pk):
    post = Post.objects.get(pk=pk)
    subscribers = post.categories.values(
        'subscribers__email', 'subscribers__username'
    )
    for subscriber in subscribers:
        html_content = render_to_string(
            'post_email.html',
            {
                'post': post,
                'username': subscriber.get("subscribers__username"),
                'domain': Site.objects.get_current().domain,
                'post_url': post.get_absolute_url(),
            }
        )

        msg = EmailMultiAlternatives(
            subject=post.title,
            body=post.text,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[subscriber.get("subscribers__email")],
            )
        msg.attach_alternative(html_content, "text/html")
        msg.send()


@shared_task
def send_weekly_email():
    last_week = datetime.today() - timedelta(days=7)
    weekly_posts = Post.objects.filter(date__gt=last_week)
    for cat in Category.objects.all():
        post_list = weekly_posts.filter(categories=cat)
        if post_list:
            subscribers = cat.subscribers.values('username', 'email')
            recipients = []
            for sub in subscribers:
                recipients.append(sub['email'])

            html_content = render_to_string(
                'weekly_email.html', {
                    'post_list': post_list.values('pk', 'title').order_by('-date'),
                    'domain': Site.objects.get_current().domain,
                }
            )

            msg = EmailMultiAlternatives(
                subject=f'Публикации за прошедшую неделю в {cat.name}',
                body="post_list",
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=recipients
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()
