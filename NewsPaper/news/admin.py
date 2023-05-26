from django.contrib import admin
from .models import *

def nullfy_rating(modeladmin, request, queryset): # все аргументы уже должны быть вам знакомы, самые нужные из них это request — объект хранящий информацию о запросе и queryset — грубо говоря набор объектов, которых мы выделили галочками.
    queryset.update(rating=0)

nullfy_rating.short_description = 'Обнулить товары' # описание для более понятного представления в админ панеле задаётся, как будто это объект


class AuthorAdmin(admin.ModelAdmin):
    # list_display — это список или кортеж со всеми полями, которые вы хотите видеть в таблице с товарами
    list_display = ('rating', 'user')
    list_filter = ('rating', 'user')
    actions = [nullfy_rating]  # добавляем действия в список


class PostAdmin(admin.ModelAdmin):
    list_display = ('type', 'date', 'title', 'rating', 'get_categories')
    list_filter = ('type',)
    search_fields = ('title', 'categories__name',)

    @staticmethod
    def get_categories(obj):
        return ', '.join(category.name for category in obj.categories.all())


admin.site.register(Author, AuthorAdmin)
admin.site.register(Category)
admin.site.register(Post, PostAdmin)
admin.site.register(Comment)

