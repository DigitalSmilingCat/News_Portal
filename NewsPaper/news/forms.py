from django import forms
from django.core.exceptions import ValidationError
from .models import *


class PostForm(forms.ModelForm):
    title = forms.CharField(label='Заголовок')
    text = forms.Textarea
    author = forms.ModelChoiceField(label='Имя автора', queryset=Author.objects.all())
    categories = forms.ModelMultipleChoiceField(label='Выберите категории', queryset=Category.objects.all())

    class Meta:
        model = Post
        fields = [
            'title',
            'text',
            'author',
            'categories',
        ]

    def clean(self):
        cleaned_data = super().clean()
        title = cleaned_data.get('title')
        if title is None:
            raise ValidationError({
                'title': 'Название не может отсутствовать.'
            })

        text = cleaned_data.get('text')
        if text is not None and len(text) < 20:
            raise ValidationError({
                'text': 'Текст не может быть менее 20 символов.'
            })
        elif text == title:
            raise ValidationError({
                'text': 'Текст не может быть идентичен названию.'
            })

        return cleaned_data
