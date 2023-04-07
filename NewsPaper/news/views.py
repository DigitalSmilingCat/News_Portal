from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Post, Author
from .filters import PostFilter
from .forms import PostForm
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin


class PostsList(ListView):
    model = Post
    ordering = '-date'
    template_name = 'posts.html'
    context_object_name = 'posts'
    paginate_by = 10

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
    paginate_by = 10

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
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['articles_quantity'] = len(Post.objects.filter(type='A'))
        return context


class PostDetail(DetailView):
    model = Post
    template_name = 'post.html'
    context_object_name = 'post'

    def get_template_names(self):
        post = self.get_object()
        if (post.type == 'N' and 'article' in self.request.path) or (post.type == 'A' and 'news' in self.request.path):
            self.template_name = '404.html'
        else:
            self.template_name = 'post.html'
        return self.template_name


class PostSearch(ListView):
    model = Post
    ordering = '-date'
    template_name = 'search.html'
    context_object_name = 'search'
    paginate_by = 10

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
        return super().form_valid(form)


class ArticleCreate(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = ('news.add_post',)
    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'

    def form_valid(self, form):
        post = form.save(commit=False)
        post.type = 'A'
        post.author = Author.objects.get(user_id=self.request.user.id)
        return super().form_valid(form)


class PostUpdate(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = ('news.change_post',)
    form_class = PostForm
    model = Post

    def get_template_names(self):
        post = self.get_object()
        if post.author == self.request.user.author:
            if (post.type == 'N' and 'news' in self.request.path) or (post.type == 'A' and 'article' in self.request.path):
                self.template_name = 'post_edit.html'
            else:
                self.template_name = '404.html'
            return self.template_name
        else:
            self.template_name = '403.html'
            return self.template_name


class PostDelete(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = ('news.delete_post',)
    model = Post
    success_url = reverse_lazy('post_list')

    def get_template_names(self):
        post = self.get_object()
        if post.author == self.request.user.author:
            if (post.type == 'N' and 'news' in self.request.path) or (post.type == 'A' and 'article' in self.request.path):
                self.template_name = 'post_delete.html'
            else:
                self.template_name = '404.html'
            return self.template_name
        else:
            self.template_name = '403.html'
            return self.template_name
