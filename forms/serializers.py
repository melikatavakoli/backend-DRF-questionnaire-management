from typing import Any
from rest_framework import serializers
from django.db import transaction
from core.choices import QuestionType
from .models import Form, Question, Option, Answer, Response


class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ["id", "text"]
        read_only_fields = ["id"]


class QuestionSerializer(serializers.ModelSerializer):
    options = OptionSerializer(many=True, required=False)

    class Meta:
        model = Question
        fields = [
            "id",
            "form",
            "max",
            "min",
            "name",
            "placeholder",
            "description",
            "category",
            "text",
            "question_type",
            "is_required",
            "order",
            "options",
        ]

    def create(self, validated_data):
        options_data = validated_data.pop("options", [])
        question = Question.objects.create(**validated_data)
        for option_data in options_data:
            Option.objects.create(question=question, **option_data)
        return question


class FormSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, required=False)

    class Meta:
        model = Form
        fields = [
            "id",
            "title",
            "type",
            "questions",
            "is_active",
        ]

    def create(self, validated_data):
        questions_data = validated_data.pop("questions", [])
        form = Form.objects.create(**validated_data)
        for question_data in questions_data:
            question_serializer = QuestionSerializer(
                data=question_data, context=self.context
            )
            question_serializer.is_valid(raise_exception=True)
            question_serializer.save(form=form)
        return form


class UserQuestionSerializer(serializers.ModelSerializer):
    options = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Question
        fields = [
            "id",
            "name",
            "max",
            "min",
            "text",
            "description",
            "category",
            "placeholder",
            "question_type",
            "is_required",
            "options",
        ]


class UserFormSerializer(serializers.ModelSerializer):
    questions = UserQuestionSerializer(many=True, read_only=True)
    _created_by = serializers.SerializerMethodField()

    class Meta:
        model = Form
        fields = ["id", "type", "title", "questions", "_created_by"]

    def get__created_by(self, obj) -> str:
        return str(obj.created_by.id) if obj.created_by else None


class AnswerSerializer(serializers.ModelSerializer):
    question = serializers.PrimaryKeyRelatedField(
        queryset=Question.objects.all()
    )
    option = serializers.PrimaryKeyRelatedField(
        queryset=Option.objects.all(), required=False
    )
    question_details = serializers.SerializerMethodField(read_only=True)
    value = serializers.CharField(
        required=False, allow_blank=True, allow_null=True
    )

    class Meta:
        model = Answer
        fields = ["question", "question_details", "value", "option"]

    def get_question_details(self, obj) -> dict[str, Any] | None:
        return UserQuestionSerializer(obj.question).data

    def validate(self, data):
        question = data["question"]
        if question.question_type in [
            QuestionType.MULTIPLE_CHOICE,
            QuestionType.CHECKBOX,
        ]:
            if not data.get("option"):
                raise serializers.ValidationError(
                    "Option is required for this question type."
                )
            if data["option"].question_id != question.id:
                raise serializers.ValidationError(
                    "Selected option does not belong to this question."
                )
        return data


class ResponseSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True)
    form_title = serializers.CharField(source="form.title", read_only=True)
    form_type = serializers.CharField(source="form.title", read_only=True)
    user_first_name = serializers.CharField(
        source="user.first_name", read_only=True
    )
    user_last_name = serializers.CharField(
        source="user.last_name", read_only=True
    )

    class Meta:
        model = Response
        fields = [
            "id",
            "form",
            "form_title",
            "user",
            "user_first_name",
            "user_last_name",
            "form_type",
            "answers",
        ]

    def validate(self, data):
        form = data["form"]
        if not form.is_active:
            raise serializers.ValidationError(
                "This form is not currently active."
            )
        required_questions = {
            str(qid)
            for qid in form.questions.filter(is_required=True).values_list(
                "id", flat=True
            )
        }
        answered_questions = {
            str(answer["question"].pk) for answer in data["answers"]
        }
        missing = set(required_questions) - answered_questions
        if missing:
            raise serializers.ValidationError(
                f"Required questions missing: {missing}"
            )
        return data

    def create(self, validated_data):
        answers_data = validated_data.pop("answers")
        with transaction.atomic():
            response = Response.objects.create(**validated_data)
            for answer_data in answers_data:
                Answer.objects.create(response=response, **answer_data)
        return response

    def update(self, instance, validated_data):
        answers_data = validated_data.pop("answers", [])
        with transaction.atomic():
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()
            existing_answers = {
                answer.question.id: answer
                for answer in instance.answers.all()
            }
            for answer_data in answers_data:
                question_id = answer_data["question"].id
                if question_id in existing_answers:
                    answer = existing_answers[question_id]
                    answer.value = answer_data["value"]
                    answer.save()
                else:
                    Answer.objects.create(response=instance, **answer_data)
        return instance


class ResponseUserSerializer(serializers.ModelSerializer):
    form_title = serializers.CharField(source="form.title", read_only=True)
    first_name = serializers.CharField(
        source="user.first_name", read_only=True
    )
    last_name = serializers.CharField(source="user.last_name", read_only=True)

    class Meta:
        model = Response
        fields = [
            "id",
            "form",
            "first_name",
            "last_name",
            "form_title",
            "user",
        ]

    def validate(self, data):
        form = data["form"]
        if not form.is_active:
            raise serializers.ValidationError(
                "This form is not currently active."
            )
        required_questions = set(
            form.questions.filter(is_required=True).values_list(
                "id", flat=True
            )
        )
        answered_questions = {
            answer["question"].id for answer in data["answers"]
        }
        missing = required_questions - answered_questions
        if missing:
            raise serializers.ValidationError(
                f"Required questions missing: {missing}"
            )
        return data

    def create(self, validated_data):
        answers_data = validated_data.pop("answers")
        with transaction.atomic():
            response = Response.objects.create(**validated_data)
            for answer_data in answers_data:
                Answer.objects.create(response=response, **answer_data)
        return response
