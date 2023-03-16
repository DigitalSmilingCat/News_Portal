from django.db import models
from django.contrib.auth.models import User  # Используется для связи Author и Comment
from django.db.models import Sum  # Используется для вычисления рейтинга автора
from news.config import *  # Используется список TYPES для поста


class Author(models.Model):  # Модель Автор
    rating = models.IntegerField(default=0)  # Рейтинг автора

    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Связь "один к одному" с встроенной моделью User

    def update_rating(self):
        articles = Post.objects.filter(author=self)  # Все статьи автора, переданного в self
        articles_rating = articles.aggregate(Sum('rating')).get('rating__sum') * 3  # Рейтинг всех статей автора * 3
        comments = Comment.objects.filter(user=self.user)  # Все комментарии автора
        comments_rating = comments.aggregate(Sum('rating')).get('rating__sum')  # Рейтинг всех комментариев автора
        post_comments = Comment.objects.filter(post__author=self)  # Все комментарии под статьями автора
        post_comments_rating = post_comments.aggregate(Sum('rating')).get('rating__sum')  # Суммарный рейтинг ком.
        self.rating = articles_rating + comments_rating + post_comments_rating  # Итоговый рейтинг
        self.save()  # Сохранение изменений

    def __str__(self):  # Изменяем метод для удобства отладки
        return f'{self.user.username} / {self.rating}'


class Category(models.Model):  # Модель Категория
    name = models.CharField(max_length=255, unique=True)  # Имя категории

    def __str__(self):  # Изменяем метод для удобства отладки
        return f'{self.name}'


class Post(models.Model):  # Модель Пост
    type = models.CharField(max_length=1, choices=TYPES, default=article)  # Тип поста (статья или новость)
    date = models.DateTimeField(auto_now_add=True)  # Дата и время создания поста
    title = models.CharField(max_length=255)  # Заголовок поста
    text = models.TextField()  # Текст поста
    rating = models.IntegerField(default=0)  # Рейтинг поста

    author = models.ForeignKey(Author, on_delete=models.CASCADE)  # Связь "один ко многим" с моделью Author
    categories = models.ManyToManyField(Category, through='PostCategory')  # Связь "многие ко многим" с Category

    def like(self):  # Метод увеличивает рейтинг на единицу
        self.rating += 1
        self.save()

    def dislike(self):  # Метод уменьшает рейтинг на единицу
        self.rating -= 1
        self.save()

    def preview(self):  # Метод выводит первые 124 символа в тексте поста, за ними следует многоточие
        return f'{self.text[:124]}...'

    def __str__(self):  # Изменяем метод для удобства отладки
        return f'{self.type} / {self.title} / {self.date} / {self.rating}'


class PostCategory(models.Model):  # Модель Пост-Категория, связывает между собой модели Post и Category
    post = models.ForeignKey(Post, on_delete=models.CASCADE)  # Связь "один ко многим" с моделью Post
    category = models.ForeignKey(Category, on_delete=models.CASCADE)  # Связь "один ко многим" с моделью Category


class Comment(models.Model):  # Модель Комментарий
    text = models.TextField()  # Текст комментария
    date = models.DateTimeField(auto_now_add=True)  # Дата и время создания комментария
    rating = models.IntegerField(default=0)  # Рейтинг комментария

    post = models.ForeignKey(Post, on_delete=models.CASCADE)  # Связь "один ко многим" с моделью Post
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Связь "один ко многим" с моделью User

    def like(self):  # Метод увеличивает рейтинг на единицу
        self.rating += 1
        self.save()

    def dislike(self):  # Метод уменьшает рейтинг на единицу
        self.rating -= 1
        self.save()
