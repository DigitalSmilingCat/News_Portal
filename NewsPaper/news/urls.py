from django.urls import path
from .views import *


urlpatterns = [
    path('', PostsList.as_view(), name='posts_list'),
    path('<int:pk>/', PostDetail.as_view(), name='post_detail'),
    path('<int:pk>/edit/', PostUpdate.as_view(), name='post_update'),
    path('<int:pk>/delete/', PostDelete.as_view(), name='post_delete'),
    path('search/', PostSearch.as_view(), name='search'),
    path('news/', NewsList.as_view(), name='news_list'),
    path('news/create/', NewsCreate.as_view(), name='news_create'),
    path('news/<int:pk>/', PostDetail.as_view(), name='news_detail'),
    path('news/<int:pk>/edit/', PostUpdate.as_view(), name='news_update'),
    path('news/<int:pk>/delete/', PostDelete.as_view(), name='news_delete'),
    path('articles/', ArticlesList.as_view(), name='articles_list'),
    path('articles/create/', ArticleCreate.as_view(), name='article_create'),
    path('articles/<int:pk>/', PostDetail.as_view(), name='article_detail'),
    path('articles/<int:pk>/edit/', PostUpdate.as_view(), name='article_update'),
    path('articles/<int:pk>/delete/', PostDelete.as_view(), name='article_delete'),
    path('categories/', CategoriesList.as_view(), name='categories'),
    path('categories/<int:pk>/', PostsInCategory.as_view(), name='posts_in_category'),
    path('categories/<int:pk>/subscribe/', subscribe, name='subscribe'),
    path('categories/<int:pk>/unsubscribe/', unsubscribe, name='unsubscribe'),
]
