from typing import Generic
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from tasks.models import Task, History, Board, Stage
from rest_framework.response import Response
from rest_framework.serializers import (
    ModelSerializer,
    EmailField,
    CharField,
    StringRelatedField,
)
from rest_framework.viewsets import ModelViewSet, mixins, GenericViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import (
    DjangoFilterBackend,
    FilterSet,
    CharFilter,
    ChoiceFilter,
    BooleanFilter,
    DateFilter,
)


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "username"]


class UserCreationSerializer(ModelSerializer):
    email = EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password")
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


# Register User
class UserCreation(mixins.CreateModelMixin, GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserCreationSerializer
    permission_classes = (AllowAny,)


# Get user via token
class UserGet(mixins.ListModelMixin, GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserCreationSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return User.objects.filter(username=self.request.user.username)


class BoardSerializer(ModelSerializer):
    title = CharField(min_length=3, max_length=255)

    class Meta:
        model = Board
        fields = ["id", "title", "description"]


class StageSerializer(ModelSerializer):
    title = CharField(min_length=3, max_length=255)
    board_name = StringRelatedField(source="board", read_only=True)

    class Meta:
        model = Stage
        fields = ["id", "title", "description", "board_name"]


class TaskSerializer(ModelSerializer):
    stage_name = StringRelatedField(source="stage", read_only=True)

    class Meta:
        model = Task
        fields = ["title", "description", "priority", "completed", "stage_name"]


class HistorySerializer(ModelSerializer):
    class Meta:
        model = History
        fields = ["task", "previous_status", "new_status", "changed_at"]


class TaskFilter(FilterSet):
    title = CharFilter(lookup_expr="icontains")
    completed = BooleanFilter()


class HistoryFilter(FilterSet):
    changed_at = DateFilter()
    previous_status = ChoiceFilter(choices=Task.STATUS_CHOICES)
    new_status = ChoiceFilter(choices=Task.STATUS_CHOICES)


class BoardViewSet(ModelViewSet):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Board.objects.filter(deleted=False, created_by=self.request.user)

    def perform_create(self, serializer):
        # serializer.user = self.request.user
        # serializer.save()
        serializer.save(created_by=self.request.user)


class StageViewset(ModelViewSet):
    queryset = Stage.objects.all()
    serializer_class = StageSerializer

    def get_queryset(self):
        # from nested router doc
        # __ looks into the field of the foreign key
        return Stage.objects.filter(
            deleted=False, board=self.kwargs["board_pk"], created_by=self.request.user
        )

    def perform_create(self, serializer):
        # serializer.user = self.request.user
        # serializer.save()
        board = get_object_or_404(
            Board.objects.filter(
                id=self.kwargs["board_pk"], created_by=self.request.user
            )
        )
        serializer.save(created_by=self.request.user, board=board)


class StageListView(mixins.ListModelMixin, GenericViewSet):
    queryset = Stage.objects.all()
    serializer_class = StageSerializer

    def get_queryset(self):
        # from nested router doc
        # __ looks into the field of the foreign key
        return Stage.objects.filter(deleted=False, created_by=self.request.user)


class TaskViewSet(ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TaskFilter

    def get_queryset(self):
        return Task.objects.filter(
            deleted=False, stage=self.kwargs["stage_pk"], user=self.request.user
        ).order_by("priority")

    def perform_create(self, serializer):
        stage = get_object_or_404(
            Stage.objects.filter(
                id=self.kwargs["stage_pk"], created_by=self.request.user
            )
        )
        serializer.save(user=self.request.user, stage=stage)


class HistroryViewSet(mixins.ListModelMixin, GenericViewSet):
    queryset = History.objects.all()
    serializer_class = HistorySerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = HistoryFilter

    def get_queryset(self):
        # from nested router doc
        # __ looks into the field of the foreign key
        return History.objects.filter(
            task=self.kwargs["task_pk"], task__user=self.request.user
        )
