from django.shortcuts import render, get_object_or_404 # type: ignore
from django.views.generic import ( # type: ignore
    CreateView, DeleteView, DetailView, UpdateView, ListView
 ) 
from django.urls import reverse_lazy, reverse # type: ignore
from django.contrib.auth.decorators import login_required # type: ignore
from django.http import HttpResponse # type: ignore
from django.contrib.auth.mixins import LoginRequiredMixin # type: ignore
from django.utils import timezone
from django.db.models import Count

from .models import Post, Category, User, Comment
from .forms import PostForm, UserForm, CommentForm

PAGINATE_NUMBER = 10


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)
    
    def get_success_url(self):
        username = self.request.user
        return reverse("blog:profile", kwargs={"username": username})


class PostListView(ListView):
    model = Post
    ordering = 'id'
    paginate_by = PAGINATE_NUMBER

    def get_queryset(self):
        return (
            Post.objects.select_related(
                'category', 'location', 'author'
            ).annotate(
                comment_count=Count('comments')
            ).filter(
                is_published=True,
                category__is_published=True,
                pub_date__lte=timezone.now()
            )
        ).order_by('-pub_date')


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        # Получаем объект по первичному ключу и автору или вызываем 404 ошибку.
        get_object_or_404(Post, pk=kwargs['post_id'], author=request.user)
        # Если объект был найден, то вызываем родительский метод, 
        # чтобы работа CBV продолжилась.
        return super().dispatch(request, *args, **kwargs)
    
    # Переопределяем get_success_url()
    def get_success_url(self):
        return reverse('blog:detail', args=[self.kwargs['post_id']]) 


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    success_url = reverse_lazy('post:list')

    def dispatch(self, request, *args, **kwargs):
        # Получаем объект по первичному ключу и автору или вызываем 404 ошибку.
        get_object_or_404(Post, pk=kwargs['post_id'], author=request.user)
        # Если объект был найден, то вызываем родительский метод, 
        # чтобы работа CBV продолжилась.
        return super().dispatch(request, *args, **kwargs)
    

class PostDetailView(DetailView):
    model = Post
    pk_url_kwarg = 'pk'

    def get_object(self, queryset=None):
        object = super().get_object(
            self.model.objects.select_related(
                'location', 'category', 'author'
            ),
        )
        if object.author != self.request.user:
            return get_object_or_404(
                self.model.objects.select_related(
                    'location', 'category', 'author'
                ).filter(
                    pub_date__lte=timezone.now(),
                    category__is_published=True,
                    is_published=True
                ),
                pk=self.kwargs['pk']
            )
        return object

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = (
            self.object.comments.select_related('author')
        )
        return context


class ProfileListView(ListView):
    model = Post
    template_name = "blog/profile.html"
    ordering = 'id'
    paginate_by = PAGINATE_NUMBER
    
    def get_queryset(self):
        self.author = get_object_or_404(
            User, username=self.kwargs['username']
        )
        return super().get_queryset().filter(
            author=self.author
            ).annotate(
                comment_count=Count('comments')
            ).order_by('-pub_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.author
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserForm
    template_name = "blog/user.html"

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user}
        )


class CategoryListView(ListView):
    model = Post
    template_name = 'blog/category.html'

    ordering = 'id'
    paginate_by = PAGINATE_NUMBER

    def get_queryset(self):
        category_slug = self.kwargs['category_slug']
        self.category = get_object_or_404(
            Category, slug=category_slug, is_published=True
        )
        current_date_time = timezone.now()
        return super().get_queryset().select_related(
            'location',
            'category',
            'author'
            ).filter(
                is_published=True,
                category__slug=category_slug,
                pub_date__lte=current_date_time
            ).order_by('-pub_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(
            Post, pk=self.kwargs.get('post_id')
        )
        return super().form_valid(form)

    def get_success_url(self):
        pk = self.kwargs['post_id']
        return reverse('blog:detail', kwargs={'pk': pk})


class CommentUpdateView(LoginRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_pk'

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().author != request.user:
            return reverse('blog:detail', self.kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('blog:detail', args=[self.kwargs['post_id']])


class CommentDeleteView(LoginRequiredMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_pk'

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().author != request.user:
            return reverse('blog:detail', post_id=self.kwargs['post_id'])
        get_object_or_404(
            Post,
            pk=self.kwargs['post_id'],
            pub_date__lte=timezone.now(),
            is_published=True,
            category__is_published=True,
        )
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        pk = self.kwargs['post_id']
        return reverse('blog:detail', kwargs={'post_id': pk})


@login_required
def simple_view(request):
    return HttpResponse('Страница для залогиненных пользователей!')