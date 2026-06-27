from django.shortcuts import get_object_or_404
from rest_framework.viewsets import ModelViewSet
from .serializers import (
    FormSerializer,
    UserFormSerializer,
    ResponseSerializer,
    QuestionSerializer,
    ResponseUserSerializer,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.filters import OrderingFilter, SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from forms.models import Response as ResponseModel
from .models import Form, Question, Option


class AdminFormViewSet(viewsets.ModelViewSet):
    queryset = Form.objects.all()
    serializer_class = FormSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)
    filterset_fields = ["type"]
    ordering_fields = ("_created_at", "_updated_at")
    search_fields = (
        "_created_by__first_name",
        "_created_by__last_name",
        "title",
    )

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(created_by=self.request.user)


class QuestionCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, form_id):
        form = get_object_or_404(Form, id=form_id)
        questions_data = request.data.get("questions")
        if not isinstance(questions_data, list) or not questions_data:
            return Response(
                {"detail": "Invalid or empty questions list"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = QuestionSerializer(data=questions_data, many=True)
        serializer.is_valid(raise_exception=True)
        created_questions, all_options = [], []

        for question_data in serializer.validated_data:
            options_data = question_data.pop("options", [])
            question = Question.objects.create(form=form, **question_data)
            created_questions.append(question)
            all_options.extend(
                [Option(question=question, **opt) for opt in options_data]
            )
        if all_options:
            Option.objects.bulk_create(all_options)
        response_data = QuestionSerializer(created_questions, many=True).data
        return Response(response_data, status=status.HTTP_201_CREATED)


class AdminQuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(created_by=self.request.user)


class PublicFormViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Form.objects.filter(is_active=True)
    serializer_class = UserFormSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filterset_fields = [
        "type"
    ]
    ordering_fields = ("_created_at", "_updated_at")

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, user=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


class ResponseBcViewSet(ModelViewSet):
    queryset = ResponseModel.objects.all()
    serializer_class = ResponseSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filterset_fields = [
        "user",
        "form__type",
    ]
    ordering_fields = ("_created_at", "_updated_at")

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, user=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


class ResponseViewSet(viewsets.ModelViewSet):
    queryset = ResponseModel.objects.all()
    serializer_class = ResponseSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filterset_fields = [
        "user",
        "form",
        "form__type",
    ]
    ordering_fields = ("_created_at", "_updated_at")

    def get_queryset(self):
        if self.request.user.role in ["superuser", "admin"]:
            return ResponseModel.objects.all()
        return ResponseModel.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, user=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


class ResponseUserViewSet(viewsets.ModelViewSet):
    queryset = ResponseModel.objects.all()
    serializer_class = ResponseUserSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filterset_fields = [
        "user",
        "form",
        "form__type",
    ]
    ordering_fields = ("_created_at", "_updated_at")

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, user=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)
