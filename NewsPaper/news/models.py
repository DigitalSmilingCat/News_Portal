from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum
from news.config import *
from django.urls import reverse
from django.core.cache import cache


class Author(models.Model):
    rating = models.IntegerField(default=0)

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def update_rating(self):
        articles = Post.objects.filter(author=self)  # Все статьи автора, переданного в self
        articles_rating = articles.aggregate(Sum('rating', default=0)).get('rating__sum') * 3  # Рейтинг всех статей автора * 3
        comments = Comment.objects.filter(user=self.user)  # Все комментарии автора
        comments_rating = comments.aggregate(Sum('rating', default=0)).get('rating__sum')  # Рейтинг всех комментариев автора
        post_comments = Comment.objects.filter(post__author=self)  # Все комментарии под статьями автора
        post_comments_rating = post_comments.aggregate(Sum('rating', default=0)).get('rating__sum')  # Суммарный рейтинг ком.
        self.rating = articles_rating + comments_rating + post_comments_rating  # Итоговый рейтинг
        self.save()  # Сохранение изменений

    def __str__(self):
        return f'{self.user.username} / {self.rating}'


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)

    subscribers = models.ManyToManyField(User, related_name='categories', through='CategorySubscriber')

    def __str__(self):
        return f'{self.name}'


class Post(models.Model):
    type = models.CharField(max_length=1, choices=TYPES, default=article)
    date = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=255)
    text = models.TextField()
    rating = models.IntegerField(default=0)

    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    categories = models.ManyToManyField(Category, through='PostCategory')

    class Meta:
        ordering = ['-date']

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()

    def preview(self):  # Метод выводит первые 124 символа в тексте поста, за ними следует многоточие
        return f'{self.text[:124]}...'

    def __str__(self):
        return f'{self.type} / {self.title} / {self.date} / {self.rating}'

    def get_absolute_url(self):
        return reverse('post_detail', args=[str(self.id)])

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        cache.delete(f"post-{self.pk}")


class PostCategory(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)


class CategorySubscriber(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    subscriber = models.ForeignKey(User, on_delete=models.CASCADE)


class Comment(models.Model):
    text = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(default=0)

    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()
