from __future__ import annotations

from typing import Iterable

from django.conf import settings
from django.contrib.auth import get_user_model, login
from django.contrib.auth.decorators import login_required
from django.core.paginator import Page, Paginator
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import CommentForm, PostForm, ProfileForm, UserRegistrationForm
from .models import Category, Comment, Post

User = get_user_model()


def _paginate(request: HttpRequest, objects: Iterable) -> Page:
    paginator = Paginator(objects, settings.POSTS_PER_PAGE)
    return paginator.get_page(request.GET.get("page"))


def _format_datetime_for_form(value):
    if not value:
        return None
    localized = timezone.localtime(value)
    return localized.strftime("%Y-%m-%dT%H:%M")


def _post_queryset():
    return (
        Post.objects.with_related_data()
        .with_comment_count()
        .order_by("-pub_date", "-created_at")
    )


def index(request: HttpRequest) -> HttpResponse:
    posts = _post_queryset().published()
    page_obj = _paginate(request, posts)
    return render(request, "blog/index.html", {"page_obj": page_obj})


def category_posts(request: HttpRequest, slug: str) -> HttpResponse:
    category = get_object_or_404(Category, slug=slug, is_published=True)
    posts = _post_queryset().filter(category=category).published()
    page_obj = _paginate(request, posts)
    context = {
        "category": category,
        "page_obj": page_obj,
    }
    return render(request, "blog/category.html", context)


def profile(request: HttpRequest, username: str) -> HttpResponse:
    profile_user = get_object_or_404(User, username=username)
    posts = _post_queryset().authored_by(profile_user)
    if profile_user != request.user:
        posts = posts.published()
    page_obj = _paginate(request, posts)
    context = {
        "profile": profile_user,
        "page_obj": page_obj,
    }
    return render(request, "blog/profile.html", context)


def post_detail(request: HttpRequest, post_id: int) -> HttpResponse:
    post = get_object_or_404(_post_queryset(), pk=post_id)
    if not post.can_be_viewed_by(request.user):
        raise Http404("Публикация скрыта")
    comments = post.comments.select_related("author")
    context = {
        "post": post,
        "comments": comments,
        "form": CommentForm(),
    }
    return render(request, "blog/detail.html", context)


@login_required
def post_create(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.author = request.user
            new_post.save()
            form.save_m2m()
            return redirect("blog:profile", username=request.user.username)
    else:
        form = PostForm(
            initial={"pub_date": _format_datetime_for_form(timezone.now())}
        )
    return render(request, "blog/create.html", {"form": form})


@login_required
def post_edit(request: HttpRequest, post_id: int) -> HttpResponse:
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect("blog:post_detail", post_id=post_id)

    if request.method == "POST":
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect("blog:post_detail", post_id=post_id)
    else:
        form = PostForm(instance=post)
        form.initial["pub_date"] = _format_datetime_for_form(post.pub_date)

    context = {"form": form, "post": post}
    return render(request, "blog/create.html", context)


@login_required
def post_delete(request: HttpRequest, post_id: int) -> HttpResponse:
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect("blog:post_detail", post_id=post_id)

    if request.method == "POST":
        post.delete()
        return redirect("blog:index")

    form = PostForm(instance=post)
    form.initial["pub_date"] = _format_datetime_for_form(post.pub_date)
    return render(request, "blog/create.html", {"form": form, "post": post})


@login_required
def add_comment(request: HttpRequest, post_id: int) -> HttpResponse:
    post = get_object_or_404(Post, pk=post_id)
    if not post.can_be_viewed_by(request.user) and post.author != request.user:
        raise Http404("Публикация скрыта")

    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
        return redirect("blog:post_detail", post_id=post_id)

    comments = post.comments.select_related("author")
    context = {
        "post": post,
        "comments": comments,
        "form": form,
    }
    return render(request, "blog/detail.html", context)


@login_required
def edit_comment(
    request: HttpRequest,
    post_id: int,
    comment_id: int,
) -> HttpResponse:
    comment = get_object_or_404(Comment, pk=comment_id, post_id=post_id)
    if comment.author != request.user:
        return redirect("blog:post_detail", post_id=post_id)

    if request.method == "POST":
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect("blog:post_detail", post_id=post_id)
    else:
        form = CommentForm(instance=comment)

    context = {"form": form, "comment": comment}
    return render(request, "blog/comment.html", context)


@login_required
def delete_comment(
    request: HttpRequest,
    post_id: int,
    comment_id: int,
) -> HttpResponse:
    comment = get_object_or_404(Comment, pk=comment_id, post_id=post_id)
    if comment.author != request.user:
        return redirect("blog:post_detail", post_id=post_id)

    if request.method == "POST":
        comment.delete()
        return redirect("blog:post_detail", post_id=post_id)

    context = {"comment": comment}
    return render(request, "blog/comment.html", context)


@login_required
def edit_profile(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("blog:profile", username=request.user.username)
    else:
        form = ProfileForm(instance=request.user)
    context = {"form": form}
    return render(request, "blog/user.html", context)


def register(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("blog:index")
    else:
        form = UserRegistrationForm()
    context = {"form": form}
    return render(request, "registration/registration_form.html", context)
