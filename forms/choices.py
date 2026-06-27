from django.db import models


class FormType(models.TextChoices):
    BMC = "bmc", "Business Model Canvas"
    SURVEY = "survey", "Survey"
    QUESTIONNAIRE = "questionnaire", "Questionnaire"
    FEEDBACK = "feedback", "Feedback"


class QuestionType(models.TextChoices):
    TEXT = "text", "Text"
    TEXTAREA = "textarea", "Textarea"
    NUMBER = "number", "Number"
    EMAIL = "email", "Email"
    PHONE = "phone", "Phone"
    DATE = "date", "Date"
    MULTIPLE_CHOICE = "multiple_choice", "Multiple Choice"
    CHECKBOX = "checkbox", "Checkbox"
