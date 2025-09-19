from django.contrib import messages
from django.contrib.auth import get_user_model, login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.utils import timezone
from django.db.models import Count, Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm, UserProfileForm
from .models import Category, Post, Comment


User = get_user_model()


POSTS_PER_PAGE = 10


def posts_queryset():
    """Получение постов из БД"""
    # select_related берёт связанные объекты за один запрос,
    # чтобы шаблонам не приходилось ходить в базу каждый раз
    # annotate добавляет количество комментариев к каждому посту
    return Post.objects.select_related(
        'category',
        'location',
        'author'
    ).annotate(
        comment_count=Count('comments')
    ).order_by('-pub_date')


def index(request):
    """Главная страница / Лента записей"""
    # Публикуем только доступные записи: опубликованные и без будущей даты
    qs = posts_queryset().filter(
        Q(category__is_published=True) | Q(category__isnull=True),
        is_published=True,
        pub_date__lte=timezone.now(),
    )
    paginator = Paginator(qs, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'blog/index.html', {'page_obj': page_obj})


def post_detail(request, id):
    """Отображение полного описания выбранной записи."""
    post = get_object_or_404(posts_queryset(), id=id)
    # Проверяем, можно ли показывать пост обычному пользователю
    is_public = (
        post.is_published
        and (post.category is None or post.category.is_published)
        and post.pub_date <= timezone.now()
    )
    # Автор всегда видит свою запись, даже скрытую
    is_author = request.user.is_authenticated and request.user == post.author
    if not (is_public or is_author):
        raise Http404
    comments = post.comments.select_related('author').all()
    form = CommentForm()
    context = {'post': post, 'comments': comments, 'form': form}
    return render(request, 'blog/detail.html', context)


def category_posts(request, category_slug):
    """Отображение публикаций категории"""
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )
    qs = posts_queryset().filter(
        category=category,
        is_published=True,
        pub_date__lte=timezone.now(),
    ).filter(
        Q(category__is_published=True) | Q(category__isnull=True)
    )
    paginator = Paginator(qs, POSTS_PER_PAGE)
    page_obj = paginator.get_page(request.GET.get('page'))
    context = {'category': category, 'page_obj': page_obj}
    return render(request, 'blog/category.html', context)


def _profile_posts(viewer, profile_user):
    qs = posts_queryset().filter(author=profile_user)
    # Если чужой профиль — показываем только опубликованные записи
    if viewer != profile_user:
        qs = qs.filter(
            Q(category__is_published=True) | Q(category__isnull=True),
            is_published=True,
            pub_date__lte=timezone.now(),
        )
    return qs


def profile(request, username):
    user = get_object_or_404(User, username=username)
    viewer = request.user if request.user.is_authenticated else None
    qs = _profile_posts(viewer, user)
    paginator = Paginator(qs, POSTS_PER_PAGE)
    page_obj = paginator.get_page(request.GET.get('page'))
    context = {'profile': user, 'page_obj': page_obj}
    return render(request, 'blog/profile.html', context)


@login_required
def profile_edit(request, username):
    profile_user = get_object_or_404(User, username=username)
    if request.user != profile_user:
        return redirect('blog:profile', username=profile_user.username)
    form = UserProfileForm(request.POST or None, instance=profile_user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Профиль обновлён')
        return redirect('blog:profile', username=profile_user.username)
    return render(request, 'blog/user.html', {'form': form})


@login_required
def post_create(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        messages.success(request, 'Публикация создана')
        return redirect('blog:profile', username=request.user.username)
    return render(request, 'blog/create.html', {'form': form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return redirect('blog:post_detail', id=post.id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post,
    )
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Публикация обновлена')
        return redirect('blog:post_detail', id=post.id)
    context = {'form': form, 'post': post}
    return render(request, 'blog/create.html', context)


@login_required
def post_delete(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return redirect('blog:post_detail', id=post.id)
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Публикация удалена')
        return redirect('blog:index')
    form = PostForm(instance=post)
    return render(request, 'blog/create.html', {'form': form})


@login_required
def comment_add(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        # save(commit=False) — чтобы заполнить автора и пост вручную
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
        messages.success(request, 'Комментарий добавлен')
    return redirect('blog:post_detail', id=post.id)


@login_required
def comment_edit(request, post_id, comment_id):
    post = get_object_or_404(Post, id=post_id)
    comment = get_object_or_404(Comment, id=comment_id, post=post)
    if request.user != comment.author:
        return redirect('blog:post_detail', id=post.id)
    form = CommentForm(request.POST or None, instance=comment)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Комментарий обновлён')
        return redirect('blog:post_detail', id=post.id)
    context = {'form': form, 'comment': comment}
    return render(request, 'blog/comment.html', context)


@login_required
def comment_delete(request, post_id, comment_id):
    post = get_object_or_404(Post, id=post_id)
    comment = get_object_or_404(Comment, id=comment_id, post=post)
    if request.user != comment.author:
        return redirect('blog:post_detail', id=post.id)
    if request.method == 'POST':
        comment.delete()
        messages.success(request, 'Комментарий удалён')
        return redirect('blog:post_detail', id=post.id)
    return render(request, 'blog/comment.html', {'comment': comment})


def register(request):
    if request.user.is_authenticated:
        return redirect('blog:index')
    form = UserCreationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        raw_password = form.cleaned_data.get('password1')
        user = authenticate(username=user.username, password=raw_password)
        if user is not None:
            login(request, user)
            return redirect('blog:profile', username=user.username)
        return redirect('login')
    return render(
        request,
        'registration/registration_form.html',
        {'form': form},
    )
