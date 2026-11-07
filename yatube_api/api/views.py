from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.serializers import (CommentSerializer, GroupSerializer,
                             PostSerializer, UserRegistrationSerializer)
from posts.models import Comment, Group, Post
from .permissions import IsAuthorOrReadOnly


class RegisterViewSet(viewsets.ViewSet):
    permission_classes = []

    def create(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated, IsAuthorOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsAuthorOrReadOnly]

    def get_queryset(self):
        post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        return (
            Comment.objects
            .filter(post=post)
            .select_related('post', 'author')
        )

    def perform_create(self, serializer):
        serializer.save(
            post_id=self.kwargs['post_id'],
            author=self.request.user,
        )
