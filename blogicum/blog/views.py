from django.shortcuts import render, get_object_or_404 # type: ignore
from datetime import datetime

from blog.models import Post, Category

def index(request):
    template = 'blog/index.html'
    current_date_time = datetime.now()
    post_list = Post.objects.select_related(
        'location',
        'category',
        'author'
        ).filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=current_date_time
        )[0:5]
    context = {'post_list': post_list}
    return render(request, template, context)

def post_detail(request, id):
    template = 'blog/detail.html'
    current_date_time = datetime.now()
    post = get_object_or_404(
        Post.objects.filter(
            is_published=True, 
            category__is_published=True,
            pub_date__lte=current_date_time
        ),
        id=id
    )
    context = {'post': post}
    return render(request, template, context)

def category_posts(request, category_slug):
    template = 'blog/category.html'
    current_date_time = datetime.now()
    category = get_object_or_404(
        Category.objects.filter(is_published=True),
        slug=category_slug
    )
    post_list = Post.objects.select_related(
        'location',
        'category',
        'author'
        ).filter(
            is_published=True,
            category__slug=category_slug,
            pub_date__lte=current_date_time
        )
    context = {
        'post_list': post_list,
        'category': category,
    }
    return render(request, template, context)