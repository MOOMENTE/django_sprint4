from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Count, Q, QuerySet
from django.utils import timezone

User = get_user_model()


class PostQuerySet(QuerySet):
    """Encapsulates frequently used post filters."""

    def published(self) -> "PostQuerySet":
        visible_now = timezone.now()
        base = self.filter(is_published=True, pub_date__lte=visible_now)
        category_is_visible = Q(category__isnull=True) | Q(
            category__is_published=True
        )
        return base.filter(category_is_visible)

    def authored_by(self, user: User) -> "PostQuerySet":
        return self.filter(author=user)

    def with_related_data(self) -> "PostQuerySet":
        return self.select_related("author", "category", "location")

    def with_comment_count(self) -> "PostQuerySet":
        return self.annotate(comment_count=Count("comments"))


class Category(models.Model):
    title = models.CharField("Заголовок", max_length=256)
    description = models.TextField("Описание")
    slug = models.SlugField(
        "Идентификатор",
        unique=True,
        help_text=(
            "Используется в адресе страницы. Разрешены буквы латиницы, цифры, "
            "дефис и подчёркивание."
        ),
    )
    is_published = models.BooleanField(
        "Опубликовано",
        default=True,
        help_text="Снимите галочку, чтобы скрыть категорию.",
    )
    created_at = models.DateTimeField("Добавлено", auto_now_add=True)

    class Meta:
        ordering = ("title",)
        verbose_name = "категория"
        verbose_name_plural = "Категории"

    def __str__(self) -> str:
        return self.title


class Location(models.Model):
    name = models.CharField("Название места", max_length=256)
    is_published = models.BooleanField(
        "Опубликовано",
        default=True,
        help_text="Снимите галочку, чтобы скрыть местоположение.",
    )
    created_at = models.DateTimeField("Добавлено", auto_now_add=True)

    class Meta:
        ordering = ("name",)
        verbose_name = "местоположение"
        verbose_name_plural = "Местоположения"

    def __str__(self) -> str:
        return self.name


class Post(models.Model):
    title = models.CharField("Заголовок", max_length=256)
    text = models.TextField("Текст")
    pub_date = models.DateTimeField(
        "Дата и время публикации",
        default=timezone.now,
        help_text=(
            "Если указать дату в будущем, получится отложенный пост."
        ),
    )
    author = models.ForeignKey(
        User,
        verbose_name="Автор",
        related_name="posts",
        on_delete=models.CASCADE,
    )
    category = models.ForeignKey(
        Category,
        verbose_name="Категория",
        related_name="posts",
        on_delete=models.SET_NULL,
        null=True,
    )
    location = models.ForeignKey(
        Location,
        verbose_name="Местоположение",
        related_name="posts",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    image = models.ImageField(
        "Изображение",
        upload_to="posts/",
        blank=True,
    )
    is_published = models.BooleanField(
        "Опубликовано",
        default=True,
        help_text="Снимите галочку, чтобы скрыть пост.",
    )
    created_at = models.DateTimeField("Добавлено", auto_now_add=True)

    objects = PostQuerySet.as_manager()

    class Meta:
        ordering = ("-pub_date", "-created_at")
        verbose_name = "публикация"
        verbose_name_plural = "Публикации"

    def __str__(self) -> str:
        return self.title

    def can_be_viewed_by(self, user: User) -> bool:
        if user.is_authenticated and user == self.author:
            return True
        category_published = (
            self.category is None or self.category.is_published
        )
        is_public_now = self.pub_date <= timezone.now()
        return self.is_published and category_published and is_public_now


class Comment(models.Model):
    text = models.TextField("Текст")
    created_at = models.DateTimeField("Добавлено", auto_now_add=True)
    author = models.ForeignKey(
        User,
        verbose_name="Автор",
        related_name="comments",
        on_delete=models.CASCADE,
    )
    post = models.ForeignKey(
        Post,
        verbose_name="Публикация",
        related_name="comments",
        on_delete=models.CASCADE,
    )

    class Meta:
        ordering = ("created_at",)
        verbose_name = "комментарий"
        verbose_name_plural = "Комментарии"

    def __str__(self) -> str:
        return self.text[:50]
