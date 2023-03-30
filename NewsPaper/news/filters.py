from django_filters import (
    FilterSet, ModelChoiceFilter, CharFilter, ModelMultipleChoiceFilter, DateTimeFilter, NumberFilter, ChoiceFilter
)
from django import forms
from .models import *
from .config import *


class PostFilter(FilterSet):
    type = ChoiceFilter(label='Статья или новость', empty_label='Неважно', choices=TYPES)
    author = ModelChoiceFilter(label='Имя автора', empty_label='Неважно', queryset=Author.objects.all())
    title = CharFilter(label='Заголовок содержит', lookup_expr='icontains')
    date = DateTimeFilter(
        label='Дата создания после',
        widget=forms.DateInput(attrs={'type': 'date'}),
        lookup_expr='date__gt',
    )
    rating = NumberFilter(label='Рейтинг больше', lookup_expr='gt')
    categories = ModelMultipleChoiceFilter(label='Выберите категории', queryset=Category.objects.all())

    class Meta:
        model = Post
        fields = [
            'type',
            'title',
            'author',
            'rating',
            'categories',
        ]