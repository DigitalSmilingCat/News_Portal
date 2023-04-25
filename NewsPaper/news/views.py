from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Post, Author, Category
from .filters import PostFilter
from .forms import PostForm
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import HttpResponseRedirect
from django.utils.timezone import datetime
from .tasks import notify_subscribers
from django.core.cache import cache


class PostsList(ListView):
    model = Post
    ordering = '-date'
    template_name = 'posts.html'
    context_object_name = 'posts'
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['posts_quantity'] = len(Post.objects.all())
        return context


class NewsList(ListView):
    model = Post
    queryset = Post.objects.filter(type='N')
    ordering = '-date'
    template_name = 'news.html'
    context_object_name = 'news'
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['news_quantity'] = len(Post.objects.filter(type='N'))
        return context


class ArticlesList(ListView):
    model = Post
    queryset = Post.objects.filter(type='A')
    ordering = '-date'
    template_name = 'articles.html'
    context_object_name = 'articles'
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['articles_quantity'] = len(Post.objects.filter(type='A'))
        return context


class PostDetail(DetailView):
    model = Post
    context_object_name = 'post'
    queryset = Post.objects.all()

    def get_template_names(self):
        post = self.get_object()
        if (post.type == 'N' and 'article' in self.request.path) or (post.type == 'A' and 'news' in self.request.path):
            self.template_name = '404.html'
        else:
            self.template_name = 'post.html'
        return self.template_name

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post_author'] = self.get_object().author.user == self.request.user
        return context

    def get_object(self, *args, **kwargs):
        obj = cache.get(f"post-{self.kwargs['pk']}", None)
        if not obj:
            obj = super().get_object(queryset=self.queryset)
            cache.set(f"post-{self.kwargs['pk']}", obj)
        return obj


class PostSearch(ListView):
    model = Post
    ordering = '-date'
    template_name = 'search.html'
    context_object_name = 'search'
    paginate_by = 5

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = PostFilter(self.request.GET, queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset
        return context


class NewsCreate(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = ('news.add_post',)
    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'

    def form_valid(self, form):
        post = form.save(commit=False)
        post.type = 'N'
        post.author = Author.objects.get(user_id=self.request.user.id)
        post.save()
        result = super().form_valid(form)
        notify_subscribers.apply_async([self.object.pk])
        return result

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['limit_posts'] = Post.objects.filter(
            author=Author.objects.get(user_id=self.request.user.id),
            date__date=datetime.date(datetime.today())).count() >= 3
        return context


class ArticleCreate(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = ('news.add_post',)
    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'

    def form_valid(self, form):
        post = form.save(commit=False)
        post.type = 'A'
        post.author = Author.objects.get(user_id=self.request.user.id)
        post.save()
        result = super().form_valid(form)
        notify_subscribers.apply_async([self.object.pk])
        return result

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['limit_posts'] = Post.objects.filter(
            author=Author.objects.get(user_id=self.request.user.id),
            date__date=datetime.date(datetime.today())).count() >= 3
        return context


class PostUpdate(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = ('news.change_post',)
    form_class = PostForm
    model = Post

    def get_template_names(self):
        post = self.get_object()
        if post.author == self.request.user.author:
            if (post.type == 'N' and 'article' in self.request.path) or (post.type == 'A' and 'news' in self.request.path):
                self.template_name = '404.html'
            else:
                self.template_name = 'post_edit.html'
            return self.template_name
        else:
            self.template_name = '403.html'
            return self.template_name


class PostDelete(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = ('news.delete_post',)
    model = Post
    success_url = reverse_lazy('posts_list')

    def get_template_names(self):
        post = self.get_object()
        if post.author == self.request.user.author:
            if (post.type == 'N' and 'article' in self.request.path) or (post.type == 'A' and 'news' in self.request.path):
                self.template_name = '404.html'
            else:
                self.template_name = 'post_delete.html'
            return self.template_name
        else:
            self.template_name = '403.html'
            return self.template_name


class CategoriesList(ListView):
    model = Category
    queryset = Category.objects.all()
    ordering = 'name'
    template_name = 'categories.html'
    context_object_name = 'categories'


class PostsInCategory(ListView):
    model = Post
    template_name = 'posts_in_category.html'
    context_object_name = 'posts_in_category'
    paginate_by = 5

    def get_queryset(self):
        # posts_in_category = Post.objects.filter(categories=self.kwargs['pk']).order_by('-date')
        self.category = get_object_or_404(Category, id=self.kwargs['pk'])
        posts_in_category = Post.objects.filter(categories=self.category).order_by('-date')
        return posts_in_category

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = Category.objects.get(pk=self.kwargs['pk'])
        context['posts_quantity'] = len(Post.objects.filter(categories=self.kwargs['pk']))
        context['cat'] = category
        context['subscribers'] = category.subscribers.all()
        return context


@login_required
def subscribe(request, pk):
    category = Category.objects.get(pk=pk)
    category.subscribers.add(request.user.id)
    return HttpResponseRedirect(reverse('posts_in_category', args=[pk]))


@login_required
def unsubscribe(request, pk):
    category = Category.objects.get(pk=pk)
    category.subscribers.remove(request.user.id)
    return HttpResponseRedirect(reverse('posts_in_category', args=[pk]))