from django.contrib import admin

from .models import (
    Answer,
    Category,
    Comment,
    Folder,
    Like,
    Memory,
    MemoryMedia,
    Question,
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Folder)
class FolderAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "parent", "created_at")
    list_filter = ("created_at",)
    search_fields = ("name", "user__full_name", "user__phone_number")
    raw_id_fields = ("user", "parent")
    readonly_fields = ("created_at",)


class MemoryMediaInline(admin.TabularInline):
    model = MemoryMedia
    extra = 0
    fields = ("file", "media_type", "caption", "order", "is_cover")


@admin.register(Memory)
class MemoryAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "visibility", "city", "country", "folder", "created_at")
    list_filter = ("visibility", "category", "country", "created_at")
    search_fields = ("title", "story", "city", "country", "author__full_name", "author__phone_number")
    raw_id_fields = ("author", "folder")
    filter_horizontal = ("category",)
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "created_at"
    inlines = [MemoryMediaInline]


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("short_text", "author", "memory", "parent", "date")
    list_filter = ("date",)
    search_fields = ("context", "author__full_name", "memory__title")
    raw_id_fields = ("memory", "author", "parent")

    @admin.display(description="Comment")
    def short_text(self, obj):
        return obj.context[:60]


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0
    raw_id_fields = ("author",)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("short_text", "author", "memory", "date")
    list_filter = ("date",)
    search_fields = ("context", "author__full_name", "memory__title")
    raw_id_fields = ("memory", "author")
    inlines = [AnswerInline]

    @admin.display(description="Question")
    def short_text(self, obj):
        return obj.context[:60]


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ("user", "memory", "created_at")
    list_filter = ("created_at",)
    raw_id_fields = ("user", "memory")