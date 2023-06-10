from django.contrib import admin
from .models import *
from modeltranslation.admin import TranslationAdmin


def nullfy_rating(modeladmin, request, queryset):
    queryset.update(rating=0)

nullfy_rating.short_description = 'Обнулить товары'


class AuthorAdmin(admin.ModelAdmin):
    list_display = ('rating', 'user')
    list_filter = ('rating', 'user')
    actions = [nullfy_rating]


class PostAdmin(admin.ModelAdmin):
    list_display = ('type', 'date', 'title', 'rating', 'get_categories')
    list_filter = ('type',)
    search_fields = ('title', 'categories__name',)
    model = Post

    @staticmethod
    def get_categories(obj):
        return ', '.join(category.name for category in obj.categories.all())


class CategoryAdmin(TranslationAdmin):
    model = Category


admin.site.register(Author, AuthorAdmin)
admin.site.register(Category)
admin.site.register(Post, PostAdmin)
admin.site.register(Comment)

