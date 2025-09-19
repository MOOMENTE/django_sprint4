from django.contrib import admin

from .models import Category, Comment, Location, Post


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "is_published", "created_at")
    list_editable = ("is_published",)
    search_fields = ("title", "slug")
    prepopulated_fields = {"slug": ("title",)}


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ("name", "is_published", "created_at")
    list_editable = ("is_published",)
    search_fields = ("name",)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "author",
        "pub_date",
        "category",
        "location",
        "is_published",
    )
    list_editable = ("is_published", "category", "location")
    list_filter = ("category", "is_published", "pub_date")
    search_fields = ("title", "text")
    raw_id_fields = ("author",)
    date_hierarchy = "pub_date"


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("short_text", "author", "post", "created_at")
    search_fields = ("text", "author__username")
    raw_id_fields = ("author", "post")
    list_filter = ("created_at",)

    @staticmethod
    def short_text(obj):
        return obj.text[:40]
