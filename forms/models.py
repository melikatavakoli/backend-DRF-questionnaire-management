from django.db import models
from common.models import GenericModel
from django.contrib.auth import get_user_model
from forms.choices import QuestionType, FormType

User = get_user_model()


class Form(GenericModel):
    title = models.CharField(max_length=255, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    type = models.CharField(
        max_length=255, choices=FormType.choices, null=True, blank=True
    )

    class Meta:
        verbose_name_plural = "forms"
        verbose_name = "form"
        db_table = "form"

    def __str__(self):
        return self.title or f"Form {self.pk}"


class Question(GenericModel):
    form = models.ForeignKey(
        Form,
        related_name="questions",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    text = models.TextField(max_length=500, null=True, blank=True)
    placeholder = models.TextField(max_length=500, null=True, blank=True)
    description = models.TextField(max_length=500, null=True, blank=True)
    category = models.CharField(max_length=400, null=True, blank=True)
    name = models.CharField(max_length=400, null=True, blank=True)
    is_required = models.BooleanField(default=False, null=True, blank=True)
    order = models.PositiveIntegerField(default=0)
    max = models.PositiveIntegerField(null=True, blank=True)
    min = models.PositiveIntegerField(null=True, blank=True)
    question_type = models.CharField(
        max_length=50, choices=QuestionType.choices, null=True, blank=True
    )

    class Meta:
        verbose_name_plural = "questions"
        verbose_name = "question"
        db_table = "question"
        ordering = ("order", "category")

    def __str__(self):
        return self.text or f"Question {self.pk}"


class Option(GenericModel):
    question = models.ForeignKey(
        Question,
        related_name="options",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    text = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        verbose_name_plural = "options"
        verbose_name = "option"
        db_table = "option"

    def __str__(self):
        return self.text or f"Option {self.pk}"


class Response(GenericModel):
    form = models.ForeignKey(
        Form,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="responses",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="responses",
    )

    class Meta:
        verbose_name_plural = "responses"
        verbose_name = "response"
        db_table = "response"

    def __str__(self):
        return (
            self.form.title
            if self.form and self.form.title
            else f"Response {self.pk}"
        )


class Answer(GenericModel):
    response = models.ForeignKey(
        Response,
        related_name="answers",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="answers_question",
        null=True,
        blank=True,
    )
    option = models.ForeignKey(
        Option,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="answers_option",
    )
    value = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "answers"
        verbose_name = "answer"
        db_table = "answers"
        indexes = (models.Index(fields=["value"], name="answer_value_idx"),)

    def __str__(self):
        if self.value:
            return self.value
        if self.option and self.option.text:
            return self.option.text
        return f"Answer {self.pk}"
