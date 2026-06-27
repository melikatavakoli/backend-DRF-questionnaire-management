from django.contrib import admin
from .models import Form, Question, Option, Response, Answer
from import_export.admin import ExportMixin


# ================== INLINE ADMINS ==================
class OptionInline(admin.TabularInline):
    model = Option
    extra = 1
    fields = ["text"]
    show_change_link = True


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1
    fields = ["text", "question_type", "is_required", "order"]
    show_change_link = True


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0
    fields = ["question", "value", "option"]
    readonly_fields = ["question", "value", "option"]
    can_delete = False
    show_change_link = True


# ================== FORM ADMIN ==================
@admin.register(Form)
class FormAdmin(ExportMixin, admin.ModelAdmin):
    list_display = ["title", "type", "is_active", "created_at", "updated_at"]
    list_filter = ["type", "is_active", "created_at"]
    search_fields = ["title"]
    inlines = [QuestionInline]


# ================== QUESTION ADMIN ==================
@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = [
        "text",
        "form",
        "question_type",
        "is_required",
        "order",
        "category",
    ]
    list_filter = ["question_type", "is_required", "category", "form"]
    search_fields = ["text", "name", "category"]
    inlines = [OptionInline]
    ordering = ["form", "order"]


# ================== OPTION ADMIN ==================
@admin.register(Option)
class OptionAdmin(admin.ModelAdmin):
    list_display = ["text", "question"]
    list_filter = ["question__form"]
    search_fields = ["text", "question__text"]


# ================== RESPONSE ADMIN ==================
@admin.register(Response)
class ResponseAdmin(admin.ModelAdmin):
    list_display = ["id", "form", "user", "created_at", "updated_at"]
    list_filter = ["form", "user", "created_at"]
    search_fields = [
        "form__title",
        "user__email",
        "user__first_name",
        "user__last_name",
    ]
    inlines = [AnswerInline]


# ================== ANSWER ADMIN ==================
@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ["response", "question", "value", "option"]
    list_filter = ["question__form", "question__question_type"]
    search_fields = ["value", "question__text", "option__text"]
